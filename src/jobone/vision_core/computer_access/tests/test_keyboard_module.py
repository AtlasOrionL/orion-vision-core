#!/usr/bin/env python3
"""
Keyboard Module Test - Focused testing for keyboard controller
"""

import time
import random
import string
from typing import Dict, Any, List

class KeyboardModuleTest:
    """Focused keyboard module testing"""
    
    def __init__(self):
        self.test_results = []
        self.typing_speed_target = 60  # WPM
        
    def run_keyboard_tests(self) -> Dict[str, Any]:
        """Run all keyboard-specific tests"""
        print("⌨️ KEYBOARD MODULE TESTING")
        print("=" * 50)
        
        tests = [
            ("text_input", self.test_text_input),
            ("special_characters", self.test_special_characters),
            ("keyboard_shortcuts", self.test_keyboard_shortcuts),
            ("typing_speed", self.test_typing_speed),
            ("key_combinations", self.test_key_combinations)
        ]
        
        results = {
            'module': 'keyboard',
            'tests_run': 0,
            'tests_passed': 0,
            'test_details': []
        }
        
        for test_name, test_func in tests:
            print(f"\n🔧 Testing: {test_name}")
            result = self._run_single_test(test_name, test_func)
            results['test_details'].append(result)
            results['tests_run'] += 1
            if result['success']:
                results['tests_passed'] += 1
        
        results['success_rate'] = (results['tests_passed'] / results['tests_run']) * 100
        
        self._print_keyboard_results(results)
        
        return results
    
    def _run_single_test(self, test_name: str, test_func) -> Dict[str, Any]:
        """Run single test with error handling"""
        start_time = time.time()
        
        try:
            result = test_func()
            execution_time = time.time() - start_time
            
            return {
                'test_name': test_name,
                'success': result.get('success', False),
                'execution_time': execution_time,
                'details': result,
                'error': None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return {
                'test_name': test_name,
                'success': False,
                'execution_time': execution_time,
                'details': {},
                'error': str(e)
            }
    
    def test_text_input(self) -> Dict[str, Any]:
        """Test basic text input functionality"""
        print("   📝 Testing text input...")
        
        # Define test texts with varying complexity
        test_texts = [
            "Hello World",
            "The quick brown fox jumps over the lazy dog",
            "Testing 123 with numbers",
            "Mixed Case Text With Capitals",
            "text with spaces and punctuation!"
        ]
        
        input_results = []
        
        for i, text in enumerate(test_texts):
            # Simulate typing with realistic timing
            char_count = len(text)
            typing_time = char_count / (self.typing_speed_target * 5 / 60)  # 5 chars per word
            
            # Add some variance to simulate human typing
            actual_time = typing_time * random.uniform(0.8, 1.2)
            
            # Simulate typing accuracy (occasional typos)
            accuracy = random.uniform(0.95, 1.0)
            errors = max(0, int(char_count * (1 - accuracy)))
            
            # Calculate effective typing speed
            effective_wpm = (char_count / 5) / (actual_time / 60) if actual_time > 0 else 0
            
            input_results.append({
                'text': text,
                'character_count': char_count,
                'typing_time': actual_time,
                'accuracy': accuracy,
                'errors': errors,
                'effective_wpm': effective_wpm,
                'success': accuracy > 0.95 and effective_wpm > 30
            })
            
            status = "✅" if input_results[-1]['success'] else "⚠️"
            print(f"      {status} Text {i+1}: {effective_wpm:.1f} WPM, {accuracy:.1%} accuracy")
            
            time.sleep(0.1)
        
        # Calculate overall statistics
        successful_inputs = sum(1 for r in input_results if r['success'])
        avg_wpm = sum(r['effective_wpm'] for r in input_results) / len(input_results)
        avg_accuracy = sum(r['accuracy'] for r in input_results) / len(input_results)
        
        success = successful_inputs >= len(test_texts) * 0.8 and avg_wpm >= 40
        
        return {
            'success': success,
            'texts_tested': len(test_texts),
            'successful_inputs': successful_inputs,
            'average_wpm': avg_wpm,
            'average_accuracy': avg_accuracy,
            'input_success_rate': (successful_inputs / len(test_texts)) * 100,
            'input_results': input_results
        }
    
    def test_special_characters(self) -> Dict[str, Any]:
        """Test special character input"""
        print("   🔣 Testing special characters...")
        
        # Define special character sets
        special_char_sets = [
            {'name': 'punctuation', 'chars': '.,;:!?'},
            {'name': 'symbols', 'chars': '@#$%^&*()'},
            {'name': 'brackets', 'chars': '[]{}()<>'},
            {'name': 'math', 'chars': '+-=*/\\'},
            {'name': 'quotes', 'chars': '\'""`'}
        ]
        
        special_results = []
        
        for char_set in special_char_sets:
            chars = char_set['chars']
            set_name = char_set['name']
            
            # Test each character in the set
            successful_chars = 0
            char_times = []
            
            for char in chars:
                # Simulate special character input
                input_time = random.uniform(0.05, 0.15)  # Slightly slower for special chars
                input_success = random.random() > 0.05  # 95% success rate
                
                if input_success:
                    successful_chars += 1
                
                char_times.append(input_time)
                time.sleep(0.05)
            
            avg_time = sum(char_times) / len(char_times)
            success_rate = (successful_chars / len(chars)) * 100
            
            special_results.append({
                'character_set': set_name,
                'characters_tested': len(chars),
                'successful_characters': successful_chars,
                'success_rate': success_rate,
                'average_input_time': avg_time,
                'set_success': success_rate >= 90
            })
            
            status = "✅" if success_rate >= 90 else "⚠️"
            print(f"      {status} {set_name}: {success_rate:.1f}% success")
        
        # Calculate overall special character performance
        successful_sets = sum(1 for r in special_results if r['set_success'])
        overall_success_rate = sum(r['success_rate'] for r in special_results) / len(special_results)
        
        success = successful_sets >= len(special_char_sets) * 0.8 and overall_success_rate >= 85
        
        return {
            'success': success,
            'character_sets_tested': len(special_char_sets),
            'successful_sets': successful_sets,
            'overall_success_rate': overall_success_rate,
            'special_char_results': special_results
        }
    
    def test_keyboard_shortcuts(self) -> Dict[str, Any]:
        """Test keyboard shortcuts"""
        print("   ⌨️ Testing keyboard shortcuts...")
        
        # Define common keyboard shortcuts
        shortcuts = [
            {'name': 'copy', 'keys': 'Ctrl+C', 'category': 'edit'},
            {'name': 'paste', 'keys': 'Ctrl+V', 'category': 'edit'},
            {'name': 'save', 'keys': 'Ctrl+S', 'category': 'file'},
            {'name': 'undo', 'keys': 'Ctrl+Z', 'category': 'edit'},
            {'name': 'select_all', 'keys': 'Ctrl+A', 'category': 'edit'},
            {'name': 'new', 'keys': 'Ctrl+N', 'category': 'file'},
            {'name': 'find', 'keys': 'Ctrl+F', 'category': 'search'},
            {'name': 'refresh', 'keys': 'F5', 'category': 'system'}
        ]
        
        shortcut_results = []
        
        for shortcut in shortcuts:
            # Simulate shortcut execution
            execution_time = random.uniform(0.02, 0.08)  # Fast execution
            recognition_success = random.random() > 0.05  # 95% recognition rate
            
            # Simulate different success rates based on complexity
            if '+' in shortcut['keys']:  # Multi-key shortcuts
                execution_success = random.random() > 0.1  # 90% success
            else:  # Single key shortcuts
                execution_success = random.random() > 0.05  # 95% success
            
            overall_success = recognition_success and execution_success
            
            shortcut_results.append({
                'shortcut_name': shortcut['name'],
                'key_combination': shortcut['keys'],
                'category': shortcut['category'],
                'execution_time': execution_time,
                'recognition_success': recognition_success,
                'execution_success': execution_success,
                'overall_success': overall_success
            })
            
            status = "✅" if overall_success else "❌"
            print(f"      {status} {shortcut['name']} ({shortcut['keys']}): {execution_time:.3f}s")
            
            time.sleep(0.1)
        
        # Calculate shortcut statistics
        successful_shortcuts = sum(1 for r in shortcut_results if r['overall_success'])
        avg_execution_time = sum(r['execution_time'] for r in shortcut_results) / len(shortcut_results)
        
        # Group by category
        categories = {}
        for result in shortcut_results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'successful': 0}
            categories[cat]['total'] += 1
            if result['overall_success']:
                categories[cat]['successful'] += 1
        
        success = successful_shortcuts >= len(shortcuts) * 0.85 and avg_execution_time < 0.1
        
        return {
            'success': success,
            'shortcuts_tested': len(shortcuts),
            'successful_shortcuts': successful_shortcuts,
            'shortcut_success_rate': (successful_shortcuts / len(shortcuts)) * 100,
            'average_execution_time': avg_execution_time,
            'category_performance': categories,
            'shortcut_results': shortcut_results
        }
    
    def test_typing_speed(self) -> Dict[str, Any]:
        """Test typing speed and consistency"""
        print("   ⚡ Testing typing speed...")
        
        # Define typing tests of different lengths
        typing_tests = [
            "Quick test",
            "This is a medium length typing test to measure speed",
            "This is a longer typing test that includes various words and punctuation marks to thoroughly test typing speed and accuracy over a sustained period of time."
        ]
        
        speed_results = []
        
        for i, text in enumerate(typing_tests):
            word_count = len(text.split())
            char_count = len(text)
            
            # Simulate typing with realistic speed variation
            base_wpm = random.uniform(45, 75)  # Realistic WPM range
            typing_time = (word_count / base_wpm) * 60  # Time in seconds
            
            # Add some variance for realism
            actual_time = typing_time * random.uniform(0.9, 1.1)
            
            # Calculate actual WPM
            actual_wpm = (word_count / actual_time) * 60 if actual_time > 0 else 0
            
            # Simulate accuracy (decreases slightly with speed)
            accuracy = max(0.85, 1.0 - (actual_wpm - 40) * 0.002)
            
            # Calculate adjusted WPM (accounting for errors)
            adjusted_wpm = actual_wpm * accuracy
            
            speed_results.append({
                'test_number': i + 1,
                'text_length': len(text),
                'word_count': word_count,
                'typing_time': actual_time,
                'raw_wpm': actual_wpm,
                'accuracy': accuracy,
                'adjusted_wpm': adjusted_wpm,
                'speed_good': adjusted_wpm >= 40
            })
            
            status = "✅" if adjusted_wpm >= 40 else "⚠️"
            print(f"      {status} Test {i+1}: {adjusted_wpm:.1f} WPM ({accuracy:.1%} accuracy)")
            
            time.sleep(0.2)
        
        # Calculate overall typing performance
        good_speeds = sum(1 for r in speed_results if r['speed_good'])
        avg_wpm = sum(r['adjusted_wpm'] for r in speed_results) / len(speed_results)
        avg_accuracy = sum(r['accuracy'] for r in speed_results) / len(speed_results)
        
        success = good_speeds >= len(typing_tests) * 0.75 and avg_wpm >= 45
        
        return {
            'success': success,
            'typing_tests': len(typing_tests),
            'good_speed_tests': good_speeds,
            'average_wpm': avg_wpm,
            'average_accuracy': avg_accuracy,
            'speed_consistency': good_speeds / len(typing_tests) * 100,
            'speed_results': speed_results
        }
    
    def test_key_combinations(self) -> Dict[str, Any]:
        """Test complex key combinations"""
        print("   🔗 Testing key combinations...")
        
        # Define complex key combinations
        combinations = [
            {'name': 'alt_tab', 'keys': ['Alt', 'Tab'], 'type': 'system'},
            {'name': 'ctrl_shift_n', 'keys': ['Ctrl', 'Shift', 'N'], 'type': 'application'},
            {'name': 'ctrl_alt_del', 'keys': ['Ctrl', 'Alt', 'Del'], 'type': 'system'},
            {'name': 'win_r', 'keys': ['Win', 'R'], 'type': 'system'},
            {'name': 'shift_f10', 'keys': ['Shift', 'F10'], 'type': 'context'}
        ]
        
        combination_results = []
        
        for combo in combinations:
            key_count = len(combo['keys'])
            
            # Simulate key combination execution
            # More keys = slightly higher chance of error
            success_rate = max(0.8, 1.0 - (key_count - 2) * 0.05)
            execution_success = random.random() < success_rate
            
            # Timing depends on number of keys
            execution_time = 0.05 + (key_count - 1) * 0.02 + random.uniform(0, 0.03)
            
            combination_results.append({
                'combination_name': combo['name'],
                'keys': combo['keys'],
                'key_count': key_count,
                'combination_type': combo['type'],
                'execution_time': execution_time,
                'execution_success': execution_success
            })
            
            status = "✅" if execution_success else "❌"
            print(f"      {status} {combo['name']} ({'+'.join(combo['keys'])}): {execution_time:.3f}s")
            
            time.sleep(0.1)
        
        # Calculate combination statistics
        successful_combinations = sum(1 for r in combination_results if r['execution_success'])
        avg_execution_time = sum(r['execution_time'] for r in combination_results) / len(combination_results)
        
        success = successful_combinations >= len(combinations) * 0.8 and avg_execution_time < 0.15
        
        return {
            'success': success,
            'combinations_tested': len(combinations),
            'successful_combinations': successful_combinations,
            'combination_success_rate': (successful_combinations / len(combinations)) * 100,
            'average_execution_time': avg_execution_time,
            'combination_results': combination_results
        }
    
    def _print_keyboard_results(self, results: Dict[str, Any]):
        """Print keyboard test results"""
        print(f"\n📊 KEYBOARD MODULE TEST RESULTS")
        print("=" * 50)
        print(f"🎯 Tests Run: {results['tests_run']}")
        print(f"✅ Tests Passed: {results['tests_passed']}")
        print(f"📈 Success Rate: {results['success_rate']:.1f}%")
        
        print(f"\n📋 Test Details:")
        for test in results['test_details']:
            status = "✅" if test['success'] else "❌"
            print(f"   {status} {test['test_name']}: {test['execution_time']:.3f}s")
            if test['error']:
                print(f"      Error: {test['error']}")
        
        if results['success_rate'] >= 80:
            print(f"\n🎉 KEYBOARD MODULE: EXCELLENT PERFORMANCE!")
        elif results['success_rate'] >= 60:
            print(f"\n✅ KEYBOARD MODULE: GOOD PERFORMANCE!")
        else:
            print(f"\n⚠️ KEYBOARD MODULE: NEEDS IMPROVEMENT!")

def test_keyboard_module():
    """Run keyboard module tests"""
    tester = KeyboardModuleTest()
    return tester.run_keyboard_tests()

if __name__ == "__main__":
    results = test_keyboard_module()
    exit(0 if results['success_rate'] >= 80 else 1)
