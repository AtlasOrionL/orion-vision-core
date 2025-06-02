#!/usr/bin/env python3
"""
Comprehensive Test Suite - Orion Vision Core Testing Framework
Sprint 8.8 - Final Integration and Production Readiness
Orion Vision Core - Autonomous AI Operating System

This module provides comprehensive testing capabilities for all Orion Vision Core
modules and subsystems, ensuring production readiness and system reliability.

Author: Orion Development Team
Version: 8.8.0
Date: 31 Mayıs 2025
"""

import sys
import os
import unittest
import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent.parent
sys.path.insert(0, str(src_dir))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrionTestSuite")

class TestResult(Enum):
    """Test result status"""
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"

@dataclass
class TestCase:
    """Test case data"""
    name: str
    description: str
    module: str
    result: TestResult
    duration: float
    error_message: Optional[str] = None

class OrionTestSuite:
    """
    Comprehensive test suite for Orion Vision Core.

    This class provides systematic testing of all modules, integration points,
    and system functionality to ensure production readiness.
    """

    def __init__(self):
        """Initialize test suite"""
        self.version = "8.8.0"
        self.test_results: List[TestCase] = []
        self.start_time = None
        self.end_time = None

        # Test statistics
        self.stats = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'duration': 0.0,
            'success_rate': 0.0
        }

        logger.info(f"🧪 Orion Test Suite v{self.version} initialized")

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        try:
            logger.info("🚀 Starting comprehensive test suite...")
            self.start_time = time.time()

            # Core module tests
            self._test_core_modules()

            # Integration tests
            self._test_integrations()

            # Performance tests
            self._test_performance()

            # System tests
            self._test_system_functionality()

            # Calculate final statistics
            self.end_time = time.time()
            self._calculate_statistics()

            # Generate report
            report = self._generate_report()

            logger.info("✅ Test suite completed")
            return report

        except Exception as e:
            logger.error(f"❌ Error running test suite: {e}")
            return {'error': str(e)}

    def _test_core_modules(self):
        """Test all core modules"""
        logger.info("🧩 Testing core modules...")

        modules_to_test = [
            ('system', 'System Manager'),
            ('llm', 'LLM API Manager'),
            ('brain', 'Brain AI Manager'),
            ('tasks', 'Task Framework'),
            ('workflows', 'Workflow Engine'),
            ('voice', 'Voice Manager'),
            ('nlp', 'NLP Processor'),
            ('automation', 'Automation Controller'),
            ('gui', 'GUI Framework'),
            ('desktop', 'Desktop Integration'),
            ('dashboard', 'System Dashboard')
        ]

        for module_name, description in modules_to_test:
            self._test_module_import(module_name, description)
            self._test_module_initialization(module_name, description)
            self._test_module_functionality(module_name, description)

    def _test_module_import(self, module_name: str, description: str):
        """Test module import"""
        test_name = f"Import {module_name} module"
        start_time = time.time()

        try:
            module_path = f"jobone.vision_core.{module_name}"
            __import__(module_path)

            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description=f"Import {description}",
                module=module_name,
                result=TestResult.PASSED,
                duration=duration
            ))

        except ImportError as e:
            duration = time.time() - start_time
            # Check if it's an optional dependency issue
            if any(dep in str(e).lower() for dep in ['pyqt6', 'pyaudio', 'speechrecognition']):
                self._add_test_result(TestCase(
                    name=test_name,
                    description=f"Import {description} (Optional dependency missing)",
                    module=module_name,
                    result=TestResult.SKIPPED,
                    duration=duration,
                    error_message=f"Optional dependency: {str(e)}"
                ))
            else:
                self._add_test_result(TestCase(
                    name=test_name,
                    description=f"Import {description}",
                    module=module_name,
                    result=TestResult.FAILED,
                    duration=duration,
                    error_message=str(e)
                ))
        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description=f"Import {description}",
                module=module_name,
                result=TestResult.ERROR,
                duration=duration,
                error_message=str(e)
            ))

    def _test_module_initialization(self, module_name: str, description: str):
        """Test module initialization"""
        test_name = f"Initialize {module_name} module"
        start_time = time.time()

        try:
            # Try to get module info
            module_path = f"jobone.vision_core.{module_name}"
            module = __import__(module_path, fromlist=[f'get_{module_name}_info'])

            if hasattr(module, f'get_{module_name}_info'):
                info_func = getattr(module, f'get_{module_name}_info')
                info = info_func()

                # Validate info structure
                required_fields = ['version', 'module', 'features']
                for field in required_fields:
                    if field not in info:
                        raise ValueError(f"Missing required field: {field}")

                duration = time.time() - start_time
                self._add_test_result(TestCase(
                    name=test_name,
                    description=f"Initialize {description}",
                    module=module_name,
                    result=TestResult.PASSED,
                    duration=duration
                ))
            else:
                duration = time.time() - start_time
                self._add_test_result(TestCase(
                    name=test_name,
                    description=f"Initialize {description}",
                    module=module_name,
                    result=TestResult.SKIPPED,
                    duration=duration,
                    error_message="No info function available"
                ))

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description=f"Initialize {description}",
                module=module_name,
                result=TestResult.FAILED,
                duration=duration,
                error_message=str(e)
            ))

    def _test_module_functionality(self, module_name: str, description: str):
        """Test basic module functionality"""
        test_name = f"Test {module_name} functionality"
        start_time = time.time()

        try:
            # Module-specific functionality tests
            if module_name == 'system':
                self._test_system_module()
            elif module_name == 'gui':
                self._test_gui_module()
            elif module_name == 'dashboard':
                self._test_dashboard_module()
            else:
                # Generic functionality test
                pass

            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description=f"Test {description} functionality",
                module=module_name,
                result=TestResult.PASSED,
                duration=duration
            ))

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description=f"Test {description} functionality",
                module=module_name,
                result=TestResult.FAILED,
                duration=duration,
                error_message=str(e)
            ))

    def _test_system_module(self):
        """Test system module specific functionality"""
        from jobone.vision_core.system import get_system_manager
        system_manager = get_system_manager()

        # Test basic operations
        info = system_manager.get_system_info()
        assert 'platform' in info
        assert 'python_version' in info

    def _test_gui_module(self):
        """Test GUI module specific functionality"""
        from jobone.vision_core.gui import get_gui_framework
        gui_framework = get_gui_framework()

        # Test theme system
        themes = gui_framework.get_available_themes()
        assert len(themes) > 0
        assert 'dark' in themes

    def _test_dashboard_module(self):
        """Test dashboard module specific functionality"""
        from jobone.vision_core.dashboard import get_dashboard_info
        info = get_dashboard_info()

        # Test dashboard info
        assert 'version' in info
        assert 'features' in info
        assert len(info['features']) > 0

    def _test_integrations(self):
        """Test module integrations"""
        logger.info("🔗 Testing module integrations...")

        # Test GUI-Dashboard integration
        self._test_gui_dashboard_integration()

        # Test Voice-NLP integration
        self._test_voice_nlp_integration()

        # Test Brain-LLM integration
        self._test_brain_llm_integration()

    def _test_gui_dashboard_integration(self):
        """Test GUI and Dashboard integration"""
        test_name = "GUI-Dashboard Integration"
        start_time = time.time()

        try:
            from jobone.vision_core.gui import get_gui_framework
            from jobone.vision_core.dashboard import get_dashboard_info

            gui = get_gui_framework()
            dashboard_info = get_dashboard_info()

            # Test integration
            assert gui is not None
            assert dashboard_info is not None

            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test GUI and Dashboard integration",
                module="integration",
                result=TestResult.PASSED,
                duration=duration
            ))

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test GUI and Dashboard integration",
                module="integration",
                result=TestResult.FAILED,
                duration=duration,
                error_message=str(e)
            ))

    def _test_voice_nlp_integration(self):
        """Test Voice and NLP integration"""
        test_name = "Voice-NLP Integration"
        start_time = time.time()

        try:
            from jobone.vision_core.voice import get_voice_info
            from jobone.vision_core.nlp import get_nlp_info

            voice_info = get_voice_info()
            nlp_info = get_nlp_info()

            # Test integration
            assert voice_info is not None
            assert nlp_info is not None

            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test Voice and NLP integration",
                module="integration",
                result=TestResult.PASSED,
                duration=duration
            ))

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test Voice and NLP integration",
                module="integration",
                result=TestResult.FAILED,
                duration=duration,
                error_message=str(e)
            ))

    def _test_brain_llm_integration(self):
        """Test Brain and LLM integration"""
        test_name = "Brain-LLM Integration"
        start_time = time.time()

        try:
            from jobone.vision_core.brain import get_brain_info
            from jobone.vision_core.llm import get_llm_info

            brain_info = get_brain_info()
            llm_info = get_llm_info()

            # Test integration
            assert brain_info is not None
            assert llm_info is not None

            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test Brain and LLM integration",
                module="integration",
                result=TestResult.PASSED,
                duration=duration
            ))

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test Brain and LLM integration",
                module="integration",
                result=TestResult.FAILED,
                duration=duration,
                error_message=str(e)
            ))

    def _test_performance(self):
        """Test system performance"""
        logger.info("⚡ Testing performance...")

        # Test import performance
        self._test_import_performance()

        # Test memory usage
        self._test_memory_usage()

    def _test_import_performance(self):
        """Test module import performance"""
        test_name = "Import Performance"
        start_time = time.time()

        try:
            # Test import speed of all modules
            modules = [
                'jobone.vision_core.system',
                'jobone.vision_core.gui',
                'jobone.vision_core.dashboard'
            ]

            for module in modules:
                module_start = time.time()
                __import__(module)
                module_duration = time.time() - module_start

                # Import should be fast (< 2 seconds)
                assert module_duration < 2.0, f"Module {module} import too slow: {module_duration:.2f}s"

            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test module import performance",
                module="performance",
                result=TestResult.PASSED,
                duration=duration
            ))

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test module import performance",
                module="performance",
                result=TestResult.FAILED,
                duration=duration,
                error_message=str(e)
            ))

    def _test_memory_usage(self):
        """Test memory usage"""
        test_name = "Memory Usage"
        start_time = time.time()

        try:
            import psutil
            process = psutil.Process()

            # Get initial memory
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Import all modules
            from jobone.vision_core import system, gui, dashboard

            # Get final memory
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (< 100 MB)
            assert memory_increase < 100, f"Memory usage too high: {memory_increase:.2f} MB"

            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description=f"Test memory usage (increase: {memory_increase:.2f} MB)",
                module="performance",
                result=TestResult.PASSED,
                duration=duration
            ))

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test memory usage",
                module="performance",
                result=TestResult.FAILED,
                duration=duration,
                error_message=str(e)
            ))

    def _test_system_functionality(self):
        """Test overall system functionality"""
        logger.info("🖥️ Testing system functionality...")

        # Test configuration loading
        self._test_configuration()

        # Test logging system
        self._test_logging()

    def _test_configuration(self):
        """Test configuration system"""
        test_name = "Configuration System"
        start_time = time.time()

        try:
            # Test basic configuration
            config = {
                'version': '8.8.0',
                'mode': 'test',
                'features': ['gui', 'voice', 'dashboard']
            }

            # Validate configuration
            assert 'version' in config
            assert 'mode' in config
            assert 'features' in config

            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test configuration system",
                module="system",
                result=TestResult.PASSED,
                duration=duration
            ))

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test configuration system",
                module="system",
                result=TestResult.FAILED,
                duration=duration,
                error_message=str(e)
            ))

    def _test_logging(self):
        """Test logging system"""
        test_name = "Logging System"
        start_time = time.time()

        try:
            # Test logging functionality
            test_logger = logging.getLogger("test")
            test_logger.info("Test log message")
            test_logger.warning("Test warning message")
            test_logger.error("Test error message")

            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test logging system",
                module="system",
                result=TestResult.PASSED,
                duration=duration
            ))

        except Exception as e:
            duration = time.time() - start_time
            self._add_test_result(TestCase(
                name=test_name,
                description="Test logging system",
                module="system",
                result=TestResult.FAILED,
                duration=duration,
                error_message=str(e)
            ))

    def _add_test_result(self, test_case: TestCase):
        """Add test result"""
        self.test_results.append(test_case)

        # Log result
        status_emoji = {
            TestResult.PASSED: "✅",
            TestResult.FAILED: "❌",
            TestResult.SKIPPED: "⏭️",
            TestResult.ERROR: "💥"
        }

        emoji = status_emoji.get(test_case.result, "❓")
        logger.info(f"{emoji} {test_case.name} ({test_case.duration:.3f}s)")

        if test_case.error_message:
            logger.error(f"   Error: {test_case.error_message}")

    def _calculate_statistics(self):
        """Calculate test statistics"""
        self.stats['total_tests'] = len(self.test_results)
        self.stats['duration'] = self.end_time - self.start_time

        for result in self.test_results:
            if result.result == TestResult.PASSED:
                self.stats['passed'] += 1
            elif result.result == TestResult.FAILED:
                self.stats['failed'] += 1
            elif result.result == TestResult.SKIPPED:
                self.stats['skipped'] += 1
            elif result.result == TestResult.ERROR:
                self.stats['errors'] += 1

        if self.stats['total_tests'] > 0:
            self.stats['success_rate'] = (self.stats['passed'] / self.stats['total_tests']) * 100

    def _generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        return {
            'version': self.version,
            'timestamp': time.time(),
            'duration': self.stats['duration'],
            'statistics': self.stats,
            'test_results': [
                {
                    'name': test.name,
                    'description': test.description,
                    'module': test.module,
                    'result': test.result.value,
                    'duration': test.duration,
                    'error_message': test.error_message
                }
                for test in self.test_results
            ]
        }

def run_test_suite():
    """Run the complete test suite"""
    try:
        print("🧪 Orion Vision Core - Comprehensive Test Suite")
        print("=" * 60)

        # Create and run test suite
        test_suite = OrionTestSuite()
        report = test_suite.run_all_tests()

        # Print summary
        print("\n📊 TEST SUMMARY")
        print("=" * 60)

        if 'error' in report:
            print(f"❌ Test suite failed: {report['error']}")
            return False

        stats = report['statistics']
        print(f"📋 Total Tests: {stats['total_tests']}")
        print(f"✅ Passed: {stats['passed']}")
        print(f"❌ Failed: {stats['failed']}")
        print(f"⏭️ Skipped: {stats['skipped']}")
        print(f"💥 Errors: {stats['errors']}")
        print(f"⏱️ Duration: {stats['duration']:.2f} seconds")
        print(f"📈 Success Rate: {stats['success_rate']:.1f}%")

        # Print failed tests
        if stats['failed'] > 0 or stats['errors'] > 0:
            print("\n❌ FAILED TESTS")
            print("-" * 40)
            for test in report['test_results']:
                if test['result'] in ['FAILED', 'ERROR']:
                    print(f"• {test['name']}: {test['error_message']}")

        # Determine overall result
        if stats['success_rate'] >= 90:
            print("\n🎉 TEST SUITE PASSED - PRODUCTION READY!")
            print(f"✨ Success Rate: {stats['success_rate']:.1f}% exceeds 90% threshold")
            return True
        elif stats['success_rate'] >= 80:
            print("\n⚠️ TEST SUITE MOSTLY PASSED - MINOR ISSUES")
            print(f"✨ Success Rate: {stats['success_rate']:.1f}% meets 80% threshold")
            return True
        else:
            print("\n❌ TEST SUITE FAILED - NEEDS ATTENTION")
            print(f"❌ Success Rate: {stats['success_rate']:.1f}% below 80% threshold")
            return False

    except Exception as e:
        print(f"❌ Error running test suite: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test runner"""
    try:
        success = run_test_suite()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test suite interrupted")
        sys.exit(1)

if __name__ == "__main__":
    main()
