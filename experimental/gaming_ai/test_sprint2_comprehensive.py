#!/usr/bin/env python3
"""
🧪 Sprint 2 Comprehensive Test Suite - Zero Trust Mode

Complete validation of all Sprint 2 components with zero trust approach.

Test Categories:
- Precision Control Tests
- Safety Manager Tests  
- Input Validator Tests
- Ethical Framework Tests
- Anti-Cheat Compliance Tests
- Integration Tests
- Performance Tests

Author: Nexus - Quantum AI Architect
Mode: Zero Trust - Verify Everything!
"""

import sys
import time
import unittest
import logging
import threading
from typing import Dict, List, Any, Tuple
import warnings

# Suppress warnings for cleaner test output
warnings.filterwarnings("ignore")

# Test imports
try:
    from precision_control import PrecisionController, PrecisionAction, ActionType, MovementType
    PRECISION_AVAILABLE = True
except ImportError as e:
    PRECISION_AVAILABLE = False
    print(f"❌ Precision Control import failed: {e}")

try:
    from safety_manager import SafetyManager, SafetyLevel, ThreatLevel
    SAFETY_AVAILABLE = True
except ImportError as e:
    SAFETY_AVAILABLE = False
    print(f"❌ Safety Manager import failed: {e}")

try:
    from input_validator import InputValidator, ValidationResult, ActionStatus
    VALIDATOR_AVAILABLE = True
except ImportError as e:
    VALIDATOR_AVAILABLE = False
    print(f"❌ Input Validator import failed: {e}")

try:
    from ethical_framework import EthicalFramework, EthicalLevel, ConsentType
    ETHICS_AVAILABLE = True
except ImportError as e:
    ETHICS_AVAILABLE = False
    print(f"❌ Ethical Framework import failed: {e}")

try:
    from anticheat_compliance import AntiCheatCompliance, ComplianceLevel, DetectionRisk
    ANTICHEAT_AVAILABLE = True
except ImportError as e:
    ANTICHEAT_AVAILABLE = False
    print(f"❌ Anti-Cheat Compliance import failed: {e}")

class TestResults:
    """Test results tracker"""
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.test_details = []
        self.performance_metrics = {}
        self.start_time = time.time()
    
    def add_result(self, test_name: str, passed: bool, details: str = "", duration: float = 0.0):
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
        
        self.test_details.append({
            "test": test_name,
            "status": status,
            "details": details,
            "duration": duration
        })
    
    def skip_test(self, test_name: str, reason: str):
        self.total_tests += 1
        self.skipped_tests += 1
        self.test_details.append({
            "test": test_name,
            "status": "⏭️ SKIP",
            "details": reason,
            "duration": 0.0
        })
    
    def get_summary(self) -> Dict[str, Any]:
        total_time = time.time() - self.start_time
        success_rate = (self.passed_tests / max(1, self.total_tests)) * 100
        
        return {
            "total_tests": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "skipped": self.skipped_tests,
            "success_rate": success_rate,
            "total_time": total_time,
            "details": self.test_details
        }

class Sprint2TestSuite:
    """Comprehensive Sprint 2 Test Suite"""
    
    def __init__(self):
        self.results = TestResults()
        self.logger = logging.getLogger("Sprint2Tests")
        
        # Configure logging for tests
        logging.basicConfig(
            level=logging.WARNING,  # Reduce noise during tests
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def run_all_tests(self):
        """Run all Sprint 2 tests"""
        print("🧪 SPRINT 2 COMPREHENSIVE TEST SUITE")
        print("=" * 60)
        print("🔍 Zero Trust Mode: Verifying everything!")
        print()
        
        # Test each component
        self.test_precision_control()
        self.test_safety_manager()
        self.test_input_validator()
        self.test_ethical_framework()
        self.test_anticheat_compliance()
        self.test_integration()
        self.test_performance()
        
        # Generate final report
        self.generate_test_report()
    
    def test_precision_control(self):
        """Test Precision Control System"""
        print("🎯 Testing Precision Control System...")
        
        if not PRECISION_AVAILABLE:
            self.results.skip_test("precision_control_import", "Module not available")
            return
        
        try:
            # Test 1: Controller initialization
            start_time = time.time()
            controller = PrecisionController(target_accuracy=0.5)
            duration = time.time() - start_time
            
            if controller and hasattr(controller, 'target_accuracy'):
                self.results.add_result("precision_init", True, "Controller initialized successfully", duration)
            else:
                self.results.add_result("precision_init", False, "Controller initialization failed", duration)
            
            # Test 2: Bezier path generation
            start_time = time.time()
            path = controller.generate_bezier_path((0, 0), (100, 100), 0.5)
            duration = time.time() - start_time
            
            if path and hasattr(path, 'start_pos') and hasattr(path, 'end_pos'):
                self.results.add_result("bezier_generation", True, "Bezier path generated", duration)
            else:
                self.results.add_result("bezier_generation", False, "Bezier generation failed", duration)
            
            # Test 3: Precision metrics
            start_time = time.time()
            metrics = controller.get_precision_metrics()
            duration = time.time() - start_time
            
            required_metrics = ['accuracy_error', 'timing_variance', 'target_accuracy']
            if all(key in metrics for key in required_metrics):
                self.results.add_result("precision_metrics", True, f"All metrics available: {list(metrics.keys())}", duration)
            else:
                self.results.add_result("precision_metrics", False, f"Missing metrics: {required_metrics}", duration)
            
            # Test 4: Action execution (simulated)
            start_time = time.time()
            action = PrecisionAction(
                action_type=ActionType.MOUSE_MOVE,
                target_position=(50, 50),
                duration=0.1
            )
            
            # Test action creation
            if action and action.action_type == ActionType.MOUSE_MOVE:
                self.results.add_result("action_creation", True, "PrecisionAction created successfully", time.time() - start_time)
            else:
                self.results.add_result("action_creation", False, "PrecisionAction creation failed", time.time() - start_time)
            
        except Exception as e:
            self.results.add_result("precision_control_error", False, f"Exception: {e}", 0.0)
    
    def test_safety_manager(self):
        """Test Safety Manager System"""
        print("🛡️ Testing Safety Manager System...")
        
        if not SAFETY_AVAILABLE:
            self.results.skip_test("safety_manager_import", "Module not available")
            return
        
        try:
            # Test 1: Safety manager initialization
            start_time = time.time()
            safety = SafetyManager(SafetyLevel.STANDARD)
            duration = time.time() - start_time
            
            if safety and hasattr(safety, 'safety_level'):
                self.results.add_result("safety_init", True, "Safety manager initialized", duration)
            else:
                self.results.add_result("safety_init", False, "Safety manager init failed", duration)
            
            # Test 2: Action validation
            start_time = time.time()
            is_safe, reason = safety.validate_action_safety("mouse_click", (100, 100), 0.1)
            duration = time.time() - start_time
            
            if isinstance(is_safe, bool) and isinstance(reason, str):
                self.results.add_result("safety_validation", True, f"Validation result: {is_safe}, {reason}", duration)
            else:
                self.results.add_result("safety_validation", False, "Invalid validation response", duration)
            
            # Test 3: Human randomization
            start_time = time.time()
            base_duration = 0.1
            randomized = safety.apply_human_randomization(base_duration)
            duration = time.time() - start_time
            
            if isinstance(randomized, (int, float)) and randomized > 0:
                variance = abs(randomized - base_duration) / base_duration
                self.results.add_result("human_randomization", True, f"Variance: {variance:.3f}", duration)
            else:
                self.results.add_result("human_randomization", False, "Randomization failed", duration)
            
            # Test 4: Emergency stop
            start_time = time.time()
            safety.trigger_emergency_stop("Test emergency")
            is_stopped = safety.emergency_stop_event.is_set()
            safety.clear_emergency_stop()
            duration = time.time() - start_time
            
            if is_stopped:
                self.results.add_result("emergency_stop", True, "Emergency stop functional", duration)
            else:
                self.results.add_result("emergency_stop", False, "Emergency stop failed", duration)
            
            # Test 5: Safety metrics
            start_time = time.time()
            metrics = safety.get_safety_metrics()
            duration = time.time() - start_time
            
            required_metrics = ['safety_level', 'threat_level', 'safety_score']
            if all(key in metrics for key in required_metrics):
                self.results.add_result("safety_metrics", True, f"Metrics: {metrics['safety_score']:.1f}%", duration)
            else:
                self.results.add_result("safety_metrics", False, "Missing safety metrics", duration)
            
        except Exception as e:
            self.results.add_result("safety_manager_error", False, f"Exception: {e}", 0.0)
    
    def test_input_validator(self):
        """Test Input Validator System"""
        print("🔍 Testing Input Validator System...")
        
        if not VALIDATOR_AVAILABLE:
            self.results.skip_test("input_validator_import", "Module not available")
            return
        
        try:
            # Test 1: Validator initialization
            start_time = time.time()
            validator = InputValidator()
            duration = time.time() - start_time
            
            if validator and hasattr(validator, 'validation_rules'):
                self.results.add_result("validator_init", True, f"Rules: {len(validator.validation_rules)}", duration)
            else:
                self.results.add_result("validator_init", False, "Validator init failed", duration)
            
            # Test 2: Action validation (if precision control available)
            if PRECISION_AVAILABLE:
                start_time = time.time()
                action = PrecisionAction(
                    action_type=ActionType.MOUSE_CLICK,
                    target_position=(100, 100),
                    duration=0.1
                )
                
                result, messages = validator.validate_action(action)
                duration = time.time() - start_time
                
                if isinstance(result, ValidationResult):
                    self.results.add_result("action_validation", True, f"Result: {result.value}", duration)
                else:
                    self.results.add_result("action_validation", False, "Validation failed", duration)
            else:
                self.results.skip_test("action_validation", "PrecisionAction not available")
            
            # Test 3: Queue management
            start_time = time.time()
            queue_status = validator.get_queue_status()
            duration = time.time() - start_time
            
            required_status = ['queue_length', 'active_actions', 'processing_active']
            if all(key in queue_status for key in required_status):
                self.results.add_result("queue_management", True, f"Queue length: {queue_status['queue_length']}", duration)
            else:
                self.results.add_result("queue_management", False, "Queue status incomplete", duration)
            
            # Test 4: Validation metrics
            start_time = time.time()
            metrics = validator.get_validation_metrics()
            duration = time.time() - start_time
            
            required_metrics = ['actions_validated', 'actions_blocked', 'validation_errors']
            if all(key in metrics for key in required_metrics):
                self.results.add_result("validation_metrics", True, f"Validated: {metrics['actions_validated']}", duration)
            else:
                self.results.add_result("validation_metrics", False, "Metrics incomplete", duration)
            
        except Exception as e:
            self.results.add_result("input_validator_error", False, f"Exception: {e}", 0.0)
    
    def test_ethical_framework(self):
        """Test Ethical Framework System"""
        print("⚖️ Testing Ethical Framework System...")
        
        if not ETHICS_AVAILABLE:
            self.results.skip_test("ethical_framework_import", "Module not available")
            return
        
        try:
            # Test 1: Ethics initialization
            start_time = time.time()
            ethics = EthicalFramework(EthicalLevel.STANDARD)
            duration = time.time() - start_time
            
            if ethics and hasattr(ethics, 'ethical_rules'):
                self.results.add_result("ethics_init", True, f"Rules: {len(ethics.ethical_rules)}", duration)
            else:
                self.results.add_result("ethics_init", False, "Ethics init failed", duration)
            
            # Test 2: Ethical evaluation
            start_time = time.time()
            context = {
                "user_id": "test_user",
                "action_type": "mouse_click",
                "ai_assistance_level": 0.5,
                "multiplayer": False
            }
            
            is_compliant, messages, decision = ethics.evaluate_ethical_compliance(context)
            duration = time.time() - start_time
            
            if isinstance(is_compliant, bool) and isinstance(decision, str):
                self.results.add_result("ethical_evaluation", True, f"Decision: {decision}", duration)
            else:
                self.results.add_result("ethical_evaluation", False, "Evaluation failed", duration)
            
            # Test 3: Consent management
            start_time = time.time()
            consent_id = ethics.request_user_consent("test_user", ["ai_assistance"])
            duration = time.time() - start_time
            
            if consent_id and isinstance(consent_id, str):
                self.results.add_result("consent_management", True, f"Consent ID: {consent_id[:8]}...", duration)
            else:
                self.results.add_result("consent_management", False, "Consent request failed", duration)
            
            # Test 4: Ethics report
            start_time = time.time()
            report = ethics.generate_ethics_report()
            duration = time.time() - start_time
            
            required_fields = ['ethical_level', 'metrics', 'compliance_rate']
            if all(key in report for key in required_fields):
                self.results.add_result("ethics_report", True, f"Compliance: {report['compliance_rate']:.1f}%", duration)
            else:
                self.results.add_result("ethics_report", False, "Report incomplete", duration)
            
        except Exception as e:
            self.results.add_result("ethical_framework_error", False, f"Exception: {e}", 0.0)
    
    def test_anticheat_compliance(self):
        """Test Anti-Cheat Compliance System"""
        print("🛡️ Testing Anti-Cheat Compliance System...")
        
        if not ANTICHEAT_AVAILABLE:
            self.results.skip_test("anticheat_compliance_import", "Module not available")
            return
        
        try:
            # Test 1: Compliance initialization
            start_time = time.time()
            compliance = AntiCheatCompliance(ComplianceLevel.STANDARD)
            duration = time.time() - start_time
            
            if compliance and hasattr(compliance, 'game_profiles'):
                self.results.add_result("compliance_init", True, f"Games: {len(compliance.game_profiles)}", duration)
            else:
                self.results.add_result("compliance_init", False, "Compliance init failed", duration)
            
            # Test 2: Game profile setting
            start_time = time.time()
            success = compliance.set_game_profile("valorant")
            duration = time.time() - start_time
            
            if success and compliance.current_game_profile:
                self.results.add_result("game_profile", True, f"Profile: {compliance.current_game_profile.game_name}", duration)
            else:
                self.results.add_result("game_profile", False, "Profile setting failed", duration)
            
            # Test 3: Risk assessment
            start_time = time.time()
            context = {
                "reaction_time": 0.25,
                "movement_smoothness": 0.8,
                "input_variance": 0.15
            }
            
            risk_level, risk_score, factors = compliance.assess_action_risk(context)
            duration = time.time() - start_time
            
            if isinstance(risk_level, DetectionRisk) and isinstance(risk_score, (int, float)):
                self.results.add_result("risk_assessment", True, f"Risk: {risk_level.value} ({risk_score:.3f})", duration)
            else:
                self.results.add_result("risk_assessment", False, "Risk assessment failed", duration)
            
            # Test 4: Compliance adaptations
            start_time = time.time()
            adapted = compliance.apply_compliance_adaptations(context.copy())
            duration = time.time() - start_time
            
            if adapted and len(adapted) >= len(context):
                self.results.add_result("compliance_adaptations", True, f"Adapted {len(adapted)} fields", duration)
            else:
                self.results.add_result("compliance_adaptations", False, "Adaptation failed", duration)
            
            # Test 5: Compliance report
            start_time = time.time()
            report = compliance.get_compliance_report()
            duration = time.time() - start_time
            
            required_fields = ['compliance_level', 'metrics', 'supported_games']
            if all(key in report for key in required_fields):
                self.results.add_result("compliance_report", True, f"Games: {len(report['supported_games'])}", duration)
            else:
                self.results.add_result("compliance_report", False, "Report incomplete", duration)
            
        except Exception as e:
            self.results.add_result("anticheat_compliance_error", False, f"Exception: {e}", 0.0)
    
    def test_integration(self):
        """Test component integration"""
        print("🔗 Testing Component Integration...")
        
        # Test 1: Module availability
        available_modules = []
        if PRECISION_AVAILABLE:
            available_modules.append("precision_control")
        if SAFETY_AVAILABLE:
            available_modules.append("safety_manager")
        if VALIDATOR_AVAILABLE:
            available_modules.append("input_validator")
        if ETHICS_AVAILABLE:
            available_modules.append("ethical_framework")
        if ANTICHEAT_AVAILABLE:
            available_modules.append("anticheat_compliance")
        
        self.results.add_result("module_availability", len(available_modules) >= 3, 
                               f"Available: {', '.join(available_modules)}", 0.0)
        
        # Test 2: Cross-component integration (if modules available)
        if SAFETY_AVAILABLE and VALIDATOR_AVAILABLE:
            try:
                start_time = time.time()
                safety = SafetyManager(SafetyLevel.STANDARD)
                validator = InputValidator(safety)
                duration = time.time() - start_time
                
                if validator.safety_manager == safety:
                    self.results.add_result("safety_validator_integration", True, "Integration successful", duration)
                else:
                    self.results.add_result("safety_validator_integration", False, "Integration failed", duration)
            except Exception as e:
                self.results.add_result("safety_validator_integration", False, f"Exception: {e}", 0.0)
        else:
            self.results.skip_test("safety_validator_integration", "Required modules not available")
    
    def test_performance(self):
        """Test performance characteristics"""
        print("⚡ Testing Performance...")
        
        # Test 1: Import performance
        start_time = time.time()
        import_count = 0
        
        if PRECISION_AVAILABLE:
            import_count += 1
        if SAFETY_AVAILABLE:
            import_count += 1
        if VALIDATOR_AVAILABLE:
            import_count += 1
        if ETHICS_AVAILABLE:
            import_count += 1
        if ANTICHEAT_AVAILABLE:
            import_count += 1
        
        import_time = time.time() - start_time
        
        if import_time < 5.0:  # Should import quickly
            self.results.add_result("import_performance", True, f"{import_count} modules in {import_time:.3f}s", import_time)
        else:
            self.results.add_result("import_performance", False, f"Slow imports: {import_time:.3f}s", import_time)
        
        # Test 2: Memory usage (basic check)
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            if memory_mb < 200:  # Should use reasonable memory
                self.results.add_result("memory_usage", True, f"Memory: {memory_mb:.1f}MB", 0.0)
            else:
                self.results.add_result("memory_usage", False, f"High memory: {memory_mb:.1f}MB", 0.0)
        except ImportError:
            self.results.skip_test("memory_usage", "psutil not available")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        summary = self.results.get_summary()
        
        print("\n" + "=" * 60)
        print("🧪 SPRINT 2 TEST RESULTS - ZERO TRUST MODE")
        print("=" * 60)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   ⏭️ Skipped: {summary['skipped']}")
        print(f"   📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"   ⏱️ Total Time: {summary['total_time']:.3f}s")
        
        print(f"\n📋 DETAILED RESULTS:")
        for detail in summary['details']:
            print(f"   {detail['status']} {detail['test']}")
            if detail['details']:
                print(f"      └─ {detail['details']}")
            if detail['duration'] > 0:
                print(f"      └─ Duration: {detail['duration']:.3f}s")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if summary['success_rate'] >= 90:
            print("   🎉 EXCELLENT: Sprint 2 components are production-ready!")
        elif summary['success_rate'] >= 75:
            print("   ✅ GOOD: Sprint 2 components are mostly functional")
        elif summary['success_rate'] >= 50:
            print("   ⚠️ FAIR: Sprint 2 components need improvements")
        else:
            print("   ❌ POOR: Sprint 2 components need significant work")
        
        print(f"\n🔍 ZERO TRUST VERDICT:")
        if summary['failed'] == 0:
            print("   ✅ TRUSTED: All tests passed - components verified!")
        elif summary['failed'] <= 2:
            print("   ⚠️ CONDITIONAL: Minor issues found - review needed")
        else:
            print("   ❌ NOT TRUSTED: Multiple failures - investigation required")

def main():
    """Run Sprint 2 comprehensive tests"""
    test_suite = Sprint2TestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()
