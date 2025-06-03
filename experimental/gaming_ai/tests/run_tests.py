#!/usr/bin/env python3
"""
🎮 Gaming AI Test Runner

Modular test runner for Gaming AI components.

Sprint 1 - Task 1.4: Testing Framework
"""

import unittest
import sys
import os
import time
import logging
from io import StringIO

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class GameAITestRunner:
    """Gaming AI Test Runner with detailed reporting"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        
    def run_all_tests(self):
        """Run all Gaming AI tests"""
        print("🎮 GAMING AI TEST SUITE")
        print("=" * 60)
        print("Sprint 1 - Task 1.4: Testing Framework")
        print("Target: 90%+ test coverage")
        print("=" * 60)
        
        # Test modules to run
        test_modules = [
            'test_vision',
            'test_ocr', 
            'test_capture'
        ]
        
        overall_start = time.time()
        
        for module_name in test_modules:
            print(f"\n🔬 Running {module_name} tests...")
            self._run_module_tests(module_name)
        
        overall_time = time.time() - overall_start
        
        # Print summary
        self._print_summary(overall_time)
        
        return self.passed_tests / self.total_tests if self.total_tests > 0 else 0
    
    def _run_module_tests(self, module_name):
        """Run tests for a specific module"""
        try:
            # Import test module
            test_module = __import__(module_name)
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Run tests with custom result handler
            stream = StringIO()
            runner = unittest.TextTestRunner(
                stream=stream,
                verbosity=2,
                buffer=True
            )
            
            start_time = time.time()
            result = runner.run(suite)
            elapsed = time.time() - start_time
            
            # Store results
            self.test_results[module_name] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped),
                'time': elapsed,
                'success_rate': self._calculate_success_rate(result)
            }
            
            # Update totals
            self.total_tests += result.testsRun
            self.passed_tests += (result.testsRun - len(result.failures) - len(result.errors))
            self.failed_tests += (len(result.failures) + len(result.errors))
            self.skipped_tests += len(result.skipped)
            
            # Print module results
            self._print_module_results(module_name, result, elapsed)
            
        except ImportError as e:
            print(f"   ❌ Failed to import {module_name}: {e}")
            self.test_results[module_name] = {
                'error': str(e),
                'tests_run': 0,
                'success_rate': 0
            }
        except Exception as e:
            print(f"   ❌ Error running {module_name}: {e}")
            self.test_results[module_name] = {
                'error': str(e),
                'tests_run': 0,
                'success_rate': 0
            }
    
    def _calculate_success_rate(self, result):
        """Calculate success rate for test result"""
        if result.testsRun == 0:
            return 0
        
        successful = result.testsRun - len(result.failures) - len(result.errors)
        return (successful / result.testsRun) * 100
    
    def _print_module_results(self, module_name, result, elapsed):
        """Print results for a test module"""
        success_rate = self._calculate_success_rate(result)
        
        print(f"   📊 Results:")
        print(f"      Tests Run: {result.testsRun}")
        print(f"      Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
        print(f"      Failed: {len(result.failures)}")
        print(f"      Errors: {len(result.errors)}")
        print(f"      Skipped: {len(result.skipped)}")
        print(f"      Success Rate: {success_rate:.1f}%")
        print(f"      Time: {elapsed:.2f}s")
        
        # Print status
        if success_rate >= 90:
            print(f"   ✅ {module_name}: EXCELLENT")
        elif success_rate >= 75:
            print(f"   ⚠️ {module_name}: GOOD")
        elif success_rate >= 50:
            print(f"   🔶 {module_name}: NEEDS IMPROVEMENT")
        else:
            print(f"   ❌ {module_name}: CRITICAL ISSUES")
        
        # Print failures if any
        if result.failures:
            print(f"   🔍 Failures:")
            for test, traceback in result.failures:
                print(f"      - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print(f"   🔍 Errors:")
            for test, traceback in result.errors:
                print(f"      - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    def _print_summary(self, total_time):
        """Print overall test summary"""
        print("\n" + "=" * 60)
        print("🎯 GAMING AI TEST SUMMARY")
        print("=" * 60)
        
        overall_success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 Overall Results:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.failed_tests}")
        print(f"   Skipped: {self.skipped_tests}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        print(f"   Total Time: {total_time:.2f}s")
        
        # Module breakdown
        print(f"\n📋 Module Breakdown:")
        for module, results in self.test_results.items():
            if 'error' in results:
                print(f"   {module}: ❌ ERROR - {results['error']}")
            else:
                success_rate = results['success_rate']
                status = "✅" if success_rate >= 90 else "⚠️" if success_rate >= 75 else "❌"
                print(f"   {module}: {status} {success_rate:.1f}% ({results['tests_run']} tests)")
        
        # Sprint 1 target assessment
        print(f"\n🎯 Sprint 1 Target Assessment:")
        print(f"   Target: 90%+ test coverage")
        print(f"   Current: {overall_success_rate:.1f}%")
        
        if overall_success_rate >= 90:
            print(f"   Status: ✅ TARGET ACHIEVED!")
        elif overall_success_rate >= 75:
            print(f"   Status: ⚠️ CLOSE TO TARGET")
        else:
            print(f"   Status: ❌ NEEDS IMPROVEMENT")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if overall_success_rate >= 90:
            print(f"   - Excellent test coverage! Ready for Sprint 2")
            print(f"   - Consider adding integration tests")
            print(f"   - Maintain test quality standards")
        elif overall_success_rate >= 75:
            print(f"   - Good progress, fix failing tests")
            print(f"   - Add more edge case testing")
            print(f"   - Improve error handling tests")
        else:
            print(f"   - Critical: Fix major test failures")
            print(f"   - Review component implementations")
            print(f"   - Add basic functionality tests")
        
        print("\n🚀 Next Steps:")
        print("   1. Fix any failing tests")
        print("   2. Add integration tests")
        print("   3. Complete Sprint 1 remaining tasks")
        print("   4. Prepare for Sprint 2: Control & Actions")

def main():
    """Main test runner function"""
    # Configure logging to reduce noise during testing
    logging.basicConfig(level=logging.ERROR)
    
    # Create and run test runner
    runner = GameAITestRunner()
    success_rate = runner.run_all_tests()
    
    # Exit with appropriate code
    if success_rate >= 0.9:  # 90%+ success
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
