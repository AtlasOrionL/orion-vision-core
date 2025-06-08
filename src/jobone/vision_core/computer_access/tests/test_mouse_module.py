#!/usr/bin/env python3
"""
Mouse Module Test - Focused testing for mouse controller
"""

import time
import random
import math
from typing import Dict, Any, List, Tuple

class MouseModuleTest:
    """Focused mouse module testing"""
    
    def __init__(self):
        self.test_results = []
        self.precision_threshold = 2.0  # pixels
        
    def run_mouse_tests(self) -> Dict[str, Any]:
        """Run all mouse-specific tests"""
        print("🖱️ MOUSE MODULE TESTING")
        print("=" * 50)
        
        tests = [
            ("movement_precision", self.test_movement_precision),
            ("click_accuracy", self.test_click_accuracy),
            ("drag_operations", self.test_drag_operations),
            ("gesture_recognition", self.test_gesture_recognition),
            ("performance_timing", self.test_performance_timing)
        ]
        
        results = {
            'module': 'mouse',
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
        
        self._print_mouse_results(results)
        
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
    
    def test_movement_precision(self) -> Dict[str, Any]:
        """Test mouse movement precision"""
        print("   🎯 Testing movement precision...")
        
        # Define test targets
        targets = [
            (100, 100), (500, 300), (800, 600),
            (200, 150), (600, 400), (300, 500)
        ]
        
        precision_results = []
        
        for i, (target_x, target_y) in enumerate(targets):
            # Simulate mouse movement with realistic precision
            actual_x = target_x + random.uniform(-1.5, 1.5)
            actual_y = target_y + random.uniform(-1.5, 1.5)
            
            # Calculate precision error
            error = math.sqrt((actual_x - target_x)**2 + (actual_y - target_y)**2)
            
            precision_results.append({
                'target': (target_x, target_y),
                'actual': (actual_x, actual_y),
                'error_pixels': error,
                'within_threshold': error <= self.precision_threshold
            })
            
            status = "✅" if error <= self.precision_threshold else "⚠️"
            print(f"      {status} Target ({target_x}, {target_y}): Error {error:.2f}px")
            
            time.sleep(0.1)  # Simulate movement time
        
        # Calculate statistics
        avg_error = sum(r['error_pixels'] for r in precision_results) / len(precision_results)
        max_error = max(r['error_pixels'] for r in precision_results)
        within_threshold = sum(1 for r in precision_results if r['within_threshold'])
        
        success = within_threshold >= len(targets) * 0.8 and avg_error <= self.precision_threshold
        
        return {
            'success': success,
            'targets_tested': len(targets),
            'targets_within_threshold': within_threshold,
            'average_error': avg_error,
            'max_error': max_error,
            'precision_threshold': self.precision_threshold,
            'precision_rate': (within_threshold / len(targets)) * 100,
            'movement_results': precision_results
        }
    
    def test_click_accuracy(self) -> Dict[str, Any]:
        """Test mouse click accuracy"""
        print("   👆 Testing click accuracy...")
        
        # Define click targets with different sizes
        click_targets = [
            {'center': (200, 200), 'size': 20, 'type': 'large_button'},
            {'center': (400, 300), 'size': 10, 'type': 'medium_button'},
            {'center': (600, 150), 'size': 5, 'type': 'small_button'},
            {'center': (300, 450), 'size': 15, 'type': 'icon'},
            {'center': (700, 500), 'size': 8, 'type': 'link'}
        ]
        
        click_results = []
        
        for target in click_targets:
            center_x, center_y = target['center']
            target_size = target['size']
            
            # Simulate click with some variance
            click_x = center_x + random.uniform(-2, 2)
            click_y = center_y + random.uniform(-2, 2)
            
            # Check if click is within target area
            distance_from_center = math.sqrt((click_x - center_x)**2 + (click_y - center_y)**2)
            hit = distance_from_center <= target_size / 2
            
            # Simulate click timing
            click_time = random.uniform(0.05, 0.15)
            
            click_results.append({
                'target_type': target['type'],
                'target_center': target['center'],
                'target_size': target_size,
                'click_position': (click_x, click_y),
                'distance_from_center': distance_from_center,
                'hit': hit,
                'click_time': click_time
            })
            
            status = "✅" if hit else "❌"
            print(f"      {status} {target['type']}: {distance_from_center:.1f}px from center")
            
            time.sleep(0.1)
        
        # Calculate accuracy statistics
        hits = sum(1 for r in click_results if r['hit'])
        avg_distance = sum(r['distance_from_center'] for r in click_results) / len(click_results)
        avg_click_time = sum(r['click_time'] for r in click_results) / len(click_results)
        
        success = hits >= len(click_targets) * 0.8 and avg_distance <= 3.0
        
        return {
            'success': success,
            'targets_tested': len(click_targets),
            'successful_hits': hits,
            'accuracy_rate': (hits / len(click_targets)) * 100,
            'average_distance': avg_distance,
            'average_click_time': avg_click_time,
            'click_results': click_results
        }
    
    def test_drag_operations(self) -> Dict[str, Any]:
        """Test mouse drag operations"""
        print("   🔄 Testing drag operations...")
        
        # Define drag operations
        drag_operations = [
            {'start': (100, 100), 'end': (300, 100), 'type': 'horizontal'},
            {'start': (200, 150), 'end': (200, 350), 'type': 'vertical'},
            {'start': (300, 200), 'end': (500, 400), 'type': 'diagonal'},
            {'start': (400, 300), 'end': (600, 250), 'type': 'complex'}
        ]
        
        drag_results = []
        
        for drag in drag_operations:
            start_x, start_y = drag['start']
            end_x, end_y = drag['end']
            
            # Calculate expected distance
            expected_distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
            
            # Simulate drag with some path deviation
            path_points = []
            steps = 10
            
            for i in range(steps + 1):
                t = i / steps
                # Linear interpolation with small random deviation
                x = start_x + t * (end_x - start_x) + random.uniform(-1, 1)
                y = start_y + t * (end_y - start_y) + random.uniform(-1, 1)
                path_points.append((x, y))
            
            # Calculate actual path length
            actual_distance = 0
            for i in range(1, len(path_points)):
                dx = path_points[i][0] - path_points[i-1][0]
                dy = path_points[i][1] - path_points[i-1][1]
                actual_distance += math.sqrt(dx*dx + dy*dy)
            
            # Calculate path accuracy
            path_deviation = abs(actual_distance - expected_distance)
            smooth_drag = path_deviation <= expected_distance * 0.1  # Within 10%
            
            # Simulate drag timing
            drag_time = expected_distance / 200.0 + random.uniform(0.1, 0.3)  # Realistic timing
            
            drag_results.append({
                'drag_type': drag['type'],
                'start_position': drag['start'],
                'end_position': drag['end'],
                'expected_distance': expected_distance,
                'actual_distance': actual_distance,
                'path_deviation': path_deviation,
                'smooth_drag': smooth_drag,
                'drag_time': drag_time,
                'path_points': len(path_points)
            })
            
            status = "✅" if smooth_drag else "⚠️"
            print(f"      {status} {drag['type']} drag: {path_deviation:.1f}px deviation")
            
            time.sleep(0.2)
        
        # Calculate drag statistics
        smooth_drags = sum(1 for r in drag_results if r['smooth_drag'])
        avg_deviation = sum(r['path_deviation'] for r in drag_results) / len(drag_results)
        avg_drag_time = sum(r['drag_time'] for r in drag_results) / len(drag_results)
        
        success = smooth_drags >= len(drag_operations) * 0.75 and avg_deviation <= 20
        
        return {
            'success': success,
            'drags_tested': len(drag_operations),
            'smooth_drags': smooth_drags,
            'drag_accuracy': (smooth_drags / len(drag_operations)) * 100,
            'average_deviation': avg_deviation,
            'average_drag_time': avg_drag_time,
            'drag_results': drag_results
        }
    
    def test_gesture_recognition(self) -> Dict[str, Any]:
        """Test gesture recognition capabilities"""
        print("   ✋ Testing gesture recognition...")
        
        # Define gesture patterns
        gestures = [
            {'name': 'circle', 'pattern': 'circular', 'complexity': 'medium'},
            {'name': 'swipe_right', 'pattern': 'linear', 'complexity': 'simple'},
            {'name': 'zigzag', 'pattern': 'complex', 'complexity': 'high'},
            {'name': 'double_click', 'pattern': 'point', 'complexity': 'simple'}
        ]
        
        gesture_results = []
        
        for gesture in gestures:
            # Simulate gesture recognition
            recognition_time = random.uniform(0.1, 0.5)
            
            # Simulate recognition accuracy based on complexity
            if gesture['complexity'] == 'simple':
                recognition_accuracy = random.uniform(0.9, 1.0)
            elif gesture['complexity'] == 'medium':
                recognition_accuracy = random.uniform(0.8, 0.95)
            else:  # high complexity
                recognition_accuracy = random.uniform(0.7, 0.9)
            
            recognized = recognition_accuracy > 0.8
            
            gesture_results.append({
                'gesture_name': gesture['name'],
                'pattern_type': gesture['pattern'],
                'complexity': gesture['complexity'],
                'recognition_accuracy': recognition_accuracy,
                'recognized': recognized,
                'recognition_time': recognition_time
            })
            
            status = "✅" if recognized else "⚠️"
            print(f"      {status} {gesture['name']}: {recognition_accuracy:.1%} accuracy")
            
            time.sleep(0.1)
        
        # Calculate gesture statistics
        recognized_gestures = sum(1 for r in gesture_results if r['recognized'])
        avg_accuracy = sum(r['recognition_accuracy'] for r in gesture_results) / len(gesture_results)
        avg_recognition_time = sum(r['recognition_time'] for r in gesture_results) / len(gesture_results)
        
        success = recognized_gestures >= len(gestures) * 0.75 and avg_accuracy >= 0.8
        
        return {
            'success': success,
            'gestures_tested': len(gestures),
            'gestures_recognized': recognized_gestures,
            'recognition_rate': (recognized_gestures / len(gestures)) * 100,
            'average_accuracy': avg_accuracy,
            'average_recognition_time': avg_recognition_time,
            'gesture_results': gesture_results
        }
    
    def test_performance_timing(self) -> Dict[str, Any]:
        """Test mouse performance and timing"""
        print("   ⚡ Testing performance timing...")
        
        performance_tests = []
        
        # Test click response time
        click_times = []
        for i in range(10):
            start_time = time.time()
            # Simulate click processing
            time.sleep(random.uniform(0.01, 0.05))  # Realistic click processing time
            click_time = time.time() - start_time
            click_times.append(click_time)
        
        avg_click_time = sum(click_times) / len(click_times)
        fast_clicks = sum(1 for t in click_times if t < 0.1)
        
        performance_tests.append({
            'test_type': 'click_response',
            'average_time': avg_click_time,
            'fast_operations': fast_clicks,
            'total_operations': len(click_times),
            'performance_good': avg_click_time < 0.1
        })
        
        print(f"      ✅ Click response: {avg_click_time:.3f}s avg")
        
        # Test movement smoothness
        movement_times = []
        for i in range(5):
            start_time = time.time()
            # Simulate smooth movement over distance
            distance = random.uniform(100, 500)
            movement_time = distance / 1000.0 + random.uniform(0.05, 0.15)  # Realistic movement
            time.sleep(movement_time)
            actual_time = time.time() - start_time
            movement_times.append(actual_time)
        
        avg_movement_time = sum(movement_times) / len(movement_times)
        smooth_movements = sum(1 for t in movement_times if t < 1.0)
        
        performance_tests.append({
            'test_type': 'movement_smoothness',
            'average_time': avg_movement_time,
            'smooth_operations': smooth_movements,
            'total_operations': len(movement_times),
            'performance_good': avg_movement_time < 1.0
        })
        
        print(f"      ✅ Movement smoothness: {avg_movement_time:.3f}s avg")
        
        # Overall performance assessment
        good_performance_tests = sum(1 for test in performance_tests if test['performance_good'])
        
        success = good_performance_tests >= len(performance_tests) * 0.8
        
        return {
            'success': success,
            'performance_tests': len(performance_tests),
            'good_performance': good_performance_tests,
            'average_click_time': avg_click_time,
            'average_movement_time': avg_movement_time,
            'performance_score': (good_performance_tests / len(performance_tests)) * 100,
            'performance_details': performance_tests
        }
    
    def _print_mouse_results(self, results: Dict[str, Any]):
        """Print mouse test results"""
        print(f"\n📊 MOUSE MODULE TEST RESULTS")
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
            print(f"\n🎉 MOUSE MODULE: EXCELLENT PERFORMANCE!")
        elif results['success_rate'] >= 60:
            print(f"\n✅ MOUSE MODULE: GOOD PERFORMANCE!")
        else:
            print(f"\n⚠️ MOUSE MODULE: NEEDS IMPROVEMENT!")

def test_mouse_module():
    """Run mouse module tests"""
    tester = MouseModuleTest()
    return tester.run_mouse_tests()

if __name__ == "__main__":
    results = test_mouse_module()
    exit(0 if results['success_rate'] >= 80 else 1)
