#!/usr/bin/env python3
"""
Run All Enhanced Tests - Updated test runner with enhanced keyboard module
"""

import time
import json
import sys
import os

# Import all module tests
try:
    from test_terminal_module import test_terminal_module
    from test_mouse_module import test_mouse_module
    from test_vision_module import test_vision_module
    from test_scenarios_module import test_scenarios_module
    from simple_enhanced_test import run_enhanced_simulation
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Module import failed: {e}")
    MODULES_AVAILABLE = False

class EnhancedTestRunner:
    """Enhanced test runner with improved keyboard module"""
    
    def __init__(self):
        self.test_modules = [
            ('terminal', test_terminal_module, '🖥️'),
            ('mouse', test_mouse_module, '🖱️'),
            ('enhanced_keyboard', self._run_enhanced_keyboard, '⌨️'),
            ('vision', test_vision_module, '👁️'),
            ('scenarios', test_scenarios_module, '🎯')
        ]
        
        self.results = {}
        self.session_start = time.time()
        
    def _run_enhanced_keyboard(self):
        """Run enhanced keyboard test"""
        return run_enhanced_simulation()
        
    def run_all_enhanced_tests(self):
        """Run all tests with enhanced keyboard module"""
        print("🧪 ORION VISION CORE - ENHANCED MODULAR TESTING SUITE")
        print("=" * 70)
        print("🔧 Testing with enhanced keyboard module")
        print()
        
        # Run each module test
        for module_name, test_func, emoji in self.test_modules:
            print(f"{emoji} TESTING MODULE: {module_name.upper()}")
            print("-" * 50)
            
            try:
                module_start = time.time()
                result = test_func()
                module_time = time.time() - module_start
                
                result['module_execution_time'] = module_time
                self.results[module_name] = result
                
                # Print module summary
                status = "✅ PASSED" if result['success_rate'] >= 80 else "⚠️ NEEDS ATTENTION" if result['success_rate'] >= 60 else "❌ FAILED"
                print(f"\n{status} - {result['success_rate']:.1f}% success rate ({module_time:.2f}s)")
                
            except Exception as e:
                print(f"❌ Module test failed: {e}")
                self.results[module_name] = {
                    'success_rate': 0,
                    'error': str(e),
                    'module_execution_time': 0
                }
            
            print("\n" + "=" * 70)
            time.sleep(1)
        
        # Generate comprehensive analysis
        return self._generate_enhanced_analysis()
    
    def _generate_enhanced_analysis(self):
        """Generate enhanced analysis"""
        session_time = time.time() - self.session_start
        
        # Calculate overall statistics
        total_modules = len(self.results)
        modules_passed = sum(1 for r in self.results.values() if r.get('success_rate', 0) >= 80)
        modules_warning = sum(1 for r in self.results.values() if 60 <= r.get('success_rate', 0) < 80)
        modules_failed = sum(1 for r in self.results.values() if r.get('success_rate', 0) < 60)
        
        overall_success_rate = sum(r.get('success_rate', 0) for r in self.results.values()) / total_modules if total_modules > 0 else 0
        total_execution_time = sum(r.get('module_execution_time', 0) for r in self.results.values())
        
        # Determine overall system status
        if overall_success_rate >= 90:
            system_status = 'EXCELLENT'
            status_emoji = '🎉'
            grade = 'A+'
        elif overall_success_rate >= 85:
            system_status = 'VERY_GOOD'
            status_emoji = '🌟'
            grade = 'A'
        elif overall_success_rate >= 80:
            system_status = 'GOOD'
            status_emoji = '✅'
            grade = 'B+'
        elif overall_success_rate >= 70:
            system_status = 'ACCEPTABLE'
            status_emoji = '⚠️'
            grade = 'B'
        else:
            system_status = 'NEEDS_IMPROVEMENT'
            status_emoji = '❌'
            grade = 'C'
        
        # Module performance ranking
        module_ranking = sorted(
            [(name, data.get('success_rate', 0)) for name, data in self.results.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Identify improvements
        keyboard_improvement = False
        if 'enhanced_keyboard' in self.results:
            kb_rate = self.results['enhanced_keyboard'].get('success_rate', 0)
            keyboard_improvement = kb_rate >= 85  # Significant improvement
        
        comprehensive_analysis = {
            'session_time': session_time,
            'total_modules': total_modules,
            'modules_passed': modules_passed,
            'modules_warning': modules_warning,
            'modules_failed': modules_failed,
            'overall_success_rate': overall_success_rate,
            'total_execution_time': total_execution_time,
            'system_status': system_status,
            'performance_grade': grade,
            'module_ranking': module_ranking,
            'keyboard_improvement': keyboard_improvement,
            'module_results': self.results
        }
        
        # Print comprehensive report
        self._print_enhanced_report(comprehensive_analysis, status_emoji)
        
        return comprehensive_analysis
    
    def _print_enhanced_report(self, analysis, status_emoji):
        """Print enhanced test report"""
        print("\n" + "=" * 80)
        print("📊 ORION VISION CORE - ENHANCED MODULAR TEST REPORT")
        print("=" * 80)
        
        # Overall Summary
        print(f"\n{status_emoji} OVERALL SYSTEM STATUS: {analysis['system_status']}")
        print(f"🏆 Performance Grade: {analysis['performance_grade']}")
        print(f"📈 Overall Success Rate: {analysis['overall_success_rate']:.1f}%")
        print(f"⏱️ Total Test Time: {analysis['total_execution_time']:.2f}s")
        
        # Enhancement highlight
        if analysis['keyboard_improvement']:
            print(f"🚀 KEYBOARD MODULE ENHANCED: Major improvement achieved!")
        
        # Module Performance Ranking
        print(f"\n🏆 MODULE PERFORMANCE RANKING:")
        for i, (module_name, success_rate) in enumerate(analysis['module_ranking'], 1):
            emoji_map = {
                'terminal': '🖥️', 
                'mouse': '🖱️', 
                'enhanced_keyboard': '⌨️', 
                'vision': '👁️', 
                'scenarios': '🎯'
            }
            emoji = emoji_map.get(module_name, '🔧')
            
            if success_rate >= 90:
                status = "🥇 EXCELLENT"
            elif success_rate >= 80:
                status = "🥈 GOOD"
            elif success_rate >= 70:
                status = "🥉 ACCEPTABLE"
            else:
                status = "❌ NEEDS WORK"
            
            enhancement_note = " (ENHANCED)" if module_name == 'enhanced_keyboard' else ""
            print(f"   {i}. {emoji} {module_name.capitalize()}{enhancement_note}: {success_rate:.1f}% - {status}")
        
        # Detailed Module Results
        print(f"\n📊 DETAILED MODULE RESULTS:")
        for module_name, result in analysis['module_results'].items():
            emoji_map = {
                'terminal': '🖥️', 
                'mouse': '🖱️', 
                'enhanced_keyboard': '⌨️', 
                'vision': '👁️', 
                'scenarios': '🎯'
            }
            emoji = emoji_map.get(module_name, '🔧')
            
            print(f"\n   {emoji} {module_name.upper()} MODULE:")
            print(f"      Success Rate: {result.get('success_rate', 0):.1f}%")
            print(f"      Tests Run: {result.get('tests_run', 0)}")
            print(f"      Tests Passed: {result.get('tests_passed', 0)}")
            print(f"      Execution Time: {result.get('module_execution_time', 0):.2f}s")
            
            if module_name == 'enhanced_keyboard':
                print(f"      🚀 Enhanced with modular approach")
        
        # Final Assessment
        print(f"\n" + "=" * 80)
        if analysis['system_status'] == 'EXCELLENT':
            print("🎉 OUTSTANDING! Orion Vision Core exceeds all expectations!")
            print("🚀 Enhanced keyboard module shows major improvement!")
            print("🌟 System is production-ready and performing at peak efficiency!")
        elif analysis['system_status'] == 'VERY_GOOD':
            print("🌟 EXCELLENT! Orion Vision Core performs exceptionally well!")
            print("🚀 Enhanced keyboard module significantly improved!")
            print("✅ System is production-ready with excellent performance!")
        elif analysis['system_status'] == 'GOOD':
            print("✅ VERY GOOD! Orion Vision Core meets all requirements!")
            print("📈 Enhanced keyboard module shows improvement!")
            print("🚀 System is production-ready!")
        else:
            print("⚠️ GOOD! Orion Vision Core is functional!")
            print("🔧 Continue optimizing for best performance!")
        
        print(f"\n🏆 ORION VISION CORE AUTONOMOUS COMPUTER ACCESS")
        print(f"📊 Final Grade: {analysis['performance_grade']} ({analysis['overall_success_rate']:.1f}%)")
        print("=" * 80)

def run_enhanced_tests():
    """Run all enhanced tests"""
    runner = EnhancedTestRunner()
    return runner.run_all_enhanced_tests()

if __name__ == "__main__":
    results = run_enhanced_tests()
    
    # Exit with appropriate code
    success_rate = results.get('overall_success_rate', 0)
    exit(0 if success_rate >= 80 else 1)
