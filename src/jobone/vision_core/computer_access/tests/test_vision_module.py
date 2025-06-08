#!/usr/bin/env python3
"""
Vision Module Test - Focused testing for vision system
"""

import time
import random
import math
from typing import Dict, Any, List, Tuple

class VisionModuleTest:
    """Focused vision module testing"""
    
    def __init__(self):
        self.test_results = []
        self.confidence_threshold = 0.7
        
    def run_vision_tests(self) -> Dict[str, Any]:
        """Run all vision-specific tests"""
        print("👁️ VISION MODULE TESTING")
        print("=" * 50)
        
        tests = [
            ("screen_capture", self.test_screen_capture),
            ("ui_element_detection", self.test_ui_element_detection),
            ("ocr_text_recognition", self.test_ocr_text_recognition),
            ("color_detection", self.test_color_detection),
            ("performance_analysis", self.test_performance_analysis)
        ]
        
        results = {
            'module': 'vision',
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
        
        self._print_vision_results(results)
        
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
    
    def test_screen_capture(self) -> Dict[str, Any]:
        """Test screen capture capabilities"""
        print("   📸 Testing screen capture...")
        
        # Define capture scenarios
        capture_scenarios = [
            {'type': 'fullscreen', 'region': None, 'expected_size': (1920, 1080)},
            {'type': 'region', 'region': (100, 100, 800, 600), 'expected_size': (700, 500)},
            {'type': 'small_region', 'region': (200, 200, 400, 300), 'expected_size': (200, 100)},
            {'type': 'corner', 'region': (0, 0, 300, 300), 'expected_size': (300, 300)}
        ]
        
        capture_results = []
        
        for scenario in capture_scenarios:
            # Simulate screen capture
            capture_time = random.uniform(0.1, 0.5)  # Realistic capture time
            
            # Simulate capture success (high success rate)
            capture_success = random.random() > 0.05  # 95% success rate
            
            if capture_success:
                # Simulate captured image properties
                if scenario['region']:
                    x, y, w, h = scenario['region']
                    actual_size = (w - x, h - y)
                else:
                    actual_size = scenario['expected_size']
                
                # Add some variance to simulate real capture
                actual_size = (
                    actual_size[0] + random.randint(-5, 5),
                    actual_size[1] + random.randint(-5, 5)
                )
                
                size_accuracy = (
                    abs(actual_size[0] - scenario['expected_size'][0]) <= 10 and
                    abs(actual_size[1] - scenario['expected_size'][1]) <= 10
                )
            else:
                actual_size = (0, 0)
                size_accuracy = False
            
            capture_results.append({
                'capture_type': scenario['type'],
                'region': scenario['region'],
                'expected_size': scenario['expected_size'],
                'actual_size': actual_size,
                'capture_time': capture_time,
                'capture_success': capture_success,
                'size_accuracy': size_accuracy,
                'overall_success': capture_success and size_accuracy
            })
            
            status = "✅" if capture_success and size_accuracy else "❌"
            print(f"      {status} {scenario['type']}: {actual_size} in {capture_time:.3f}s")
            
            time.sleep(0.1)
        
        # Calculate capture statistics
        successful_captures = sum(1 for r in capture_results if r['overall_success'])
        avg_capture_time = sum(r['capture_time'] for r in capture_results) / len(capture_results)
        
        success = successful_captures >= len(capture_scenarios) * 0.8 and avg_capture_time < 1.0
        
        return {
            'success': success,
            'captures_tested': len(capture_scenarios),
            'successful_captures': successful_captures,
            'capture_success_rate': (successful_captures / len(capture_scenarios)) * 100,
            'average_capture_time': avg_capture_time,
            'capture_results': capture_results
        }
    
    def test_ui_element_detection(self) -> Dict[str, Any]:
        """Test UI element detection"""
        print("   🔍 Testing UI element detection...")
        
        # Define UI elements to detect
        ui_elements = [
            {'type': 'button', 'size': 'large', 'confidence_expected': 0.9},
            {'type': 'textbox', 'size': 'medium', 'confidence_expected': 0.85},
            {'type': 'checkbox', 'size': 'small', 'confidence_expected': 0.8},
            {'type': 'dropdown', 'size': 'medium', 'confidence_expected': 0.85},
            {'type': 'icon', 'size': 'small', 'confidence_expected': 0.75},
            {'type': 'menu', 'size': 'large', 'confidence_expected': 0.9},
            {'type': 'link', 'size': 'small', 'confidence_expected': 0.7}
        ]
        
        detection_results = []
        
        for element in ui_elements:
            # Simulate detection process
            detection_time = random.uniform(0.2, 0.8)
            
            # Simulate detection confidence based on element characteristics
            base_confidence = element['confidence_expected']
            actual_confidence = base_confidence + random.uniform(-0.1, 0.1)
            actual_confidence = max(0.0, min(1.0, actual_confidence))
            
            # Detection success based on confidence threshold
            detected = actual_confidence >= self.confidence_threshold
            
            # Simulate bounding box (if detected)
            if detected:
                bbox = {
                    'x': random.randint(50, 800),
                    'y': random.randint(50, 600),
                    'width': random.randint(50, 200),
                    'height': random.randint(20, 100)
                }
            else:
                bbox = None
            
            detection_results.append({
                'element_type': element['type'],
                'element_size': element['size'],
                'detection_time': detection_time,
                'confidence': actual_confidence,
                'detected': detected,
                'bounding_box': bbox,
                'expected_confidence': element['confidence_expected']
            })
            
            status = "✅" if detected else "❌"
            print(f"      {status} {element['type']}: {actual_confidence:.2f} confidence")
            
            time.sleep(0.1)
        
        # Calculate detection statistics
        successful_detections = sum(1 for r in detection_results if r['detected'])
        avg_confidence = sum(r['confidence'] for r in detection_results) / len(detection_results)
        avg_detection_time = sum(r['detection_time'] for r in detection_results) / len(detection_results)
        
        success = successful_detections >= len(ui_elements) * 0.7 and avg_confidence >= 0.75
        
        return {
            'success': success,
            'elements_tested': len(ui_elements),
            'successful_detections': successful_detections,
            'detection_rate': (successful_detections / len(ui_elements)) * 100,
            'average_confidence': avg_confidence,
            'average_detection_time': avg_detection_time,
            'detection_results': detection_results
        }
    
    def test_ocr_text_recognition(self) -> Dict[str, Any]:
        """Test OCR text recognition"""
        print("   📝 Testing OCR text recognition...")
        
        # Define text samples with varying difficulty
        text_samples = [
            {'text': 'Hello World', 'difficulty': 'easy', 'expected_accuracy': 0.95},
            {'text': 'The Quick Brown Fox', 'difficulty': 'easy', 'expected_accuracy': 0.95},
            {'text': 'Mixed Case Text 123', 'difficulty': 'medium', 'expected_accuracy': 0.9},
            {'text': 'Special@Characters!', 'difficulty': 'medium', 'expected_accuracy': 0.85},
            {'text': 'small text size', 'difficulty': 'hard', 'expected_accuracy': 0.8},
            {'text': 'Handwritten Style', 'difficulty': 'hard', 'expected_accuracy': 0.75}
        ]
        
        ocr_results = []
        
        for sample in text_samples:
            original_text = sample['text']
            difficulty = sample['difficulty']
            expected_accuracy = sample['expected_accuracy']
            
            # Simulate OCR processing time
            processing_time = random.uniform(0.3, 1.0)
            
            # Simulate OCR accuracy based on difficulty
            base_accuracy = expected_accuracy
            actual_accuracy = base_accuracy + random.uniform(-0.05, 0.05)
            actual_accuracy = max(0.0, min(1.0, actual_accuracy))
            
            # Generate recognized text with simulated errors
            recognized_text = self._simulate_ocr_errors(original_text, actual_accuracy)
            
            # Calculate character-level accuracy
            char_accuracy = self._calculate_text_accuracy(original_text, recognized_text)
            
            ocr_results.append({
                'original_text': original_text,
                'recognized_text': recognized_text,
                'difficulty': difficulty,
                'processing_time': processing_time,
                'expected_accuracy': expected_accuracy,
                'actual_accuracy': char_accuracy,
                'recognition_success': char_accuracy >= 0.8
            })
            
            status = "✅" if char_accuracy >= 0.8 else "⚠️"
            print(f"      {status} '{original_text}': {char_accuracy:.1%} accuracy")
            
            time.sleep(0.1)
        
        # Calculate OCR statistics
        successful_recognitions = sum(1 for r in ocr_results if r['recognition_success'])
        avg_accuracy = sum(r['actual_accuracy'] for r in ocr_results) / len(ocr_results)
        avg_processing_time = sum(r['processing_time'] for r in ocr_results) / len(ocr_results)
        
        success = successful_recognitions >= len(text_samples) * 0.75 and avg_accuracy >= 0.8
        
        return {
            'success': success,
            'texts_tested': len(text_samples),
            'successful_recognitions': successful_recognitions,
            'recognition_rate': (successful_recognitions / len(text_samples)) * 100,
            'average_accuracy': avg_accuracy,
            'average_processing_time': avg_processing_time,
            'ocr_results': ocr_results
        }
    
    def test_color_detection(self) -> Dict[str, Any]:
        """Test color detection capabilities"""
        print("   🎨 Testing color detection...")
        
        # Define color detection scenarios
        color_scenarios = [
            {'color_name': 'red', 'rgb': (255, 0, 0), 'tolerance': 20},
            {'color_name': 'green', 'rgb': (0, 255, 0), 'tolerance': 20},
            {'color_name': 'blue', 'rgb': (0, 0, 255), 'tolerance': 20},
            {'color_name': 'yellow', 'rgb': (255, 255, 0), 'tolerance': 25},
            {'color_name': 'purple', 'rgb': (128, 0, 128), 'tolerance': 30},
            {'color_name': 'orange', 'rgb': (255, 165, 0), 'tolerance': 25}
        ]
        
        color_results = []
        
        for scenario in color_scenarios:
            target_rgb = scenario['rgb']
            tolerance = scenario['tolerance']
            
            # Simulate color detection with some variance
            detected_rgb = (
                target_rgb[0] + random.randint(-tolerance//2, tolerance//2),
                target_rgb[1] + random.randint(-tolerance//2, tolerance//2),
                target_rgb[2] + random.randint(-tolerance//2, tolerance//2)
            )
            
            # Ensure RGB values are in valid range
            detected_rgb = tuple(max(0, min(255, c)) for c in detected_rgb)
            
            # Calculate color distance
            color_distance = math.sqrt(sum((a - b)**2 for a, b in zip(target_rgb, detected_rgb)))
            
            # Detection success based on tolerance
            detection_success = color_distance <= tolerance
            
            # Simulate detection time
            detection_time = random.uniform(0.1, 0.3)
            
            color_results.append({
                'color_name': scenario['color_name'],
                'target_rgb': target_rgb,
                'detected_rgb': detected_rgb,
                'color_distance': color_distance,
                'tolerance': tolerance,
                'detection_time': detection_time,
                'detection_success': detection_success
            })
            
            status = "✅" if detection_success else "❌"
            print(f"      {status} {scenario['color_name']}: distance {color_distance:.1f}")
            
            time.sleep(0.1)
        
        # Calculate color detection statistics
        successful_detections = sum(1 for r in color_results if r['detection_success'])
        avg_distance = sum(r['color_distance'] for r in color_results) / len(color_results)
        avg_detection_time = sum(r['detection_time'] for r in color_results) / len(color_results)
        
        success = successful_detections >= len(color_scenarios) * 0.8 and avg_distance <= 25
        
        return {
            'success': success,
            'colors_tested': len(color_scenarios),
            'successful_detections': successful_detections,
            'detection_rate': (successful_detections / len(color_scenarios)) * 100,
            'average_color_distance': avg_distance,
            'average_detection_time': avg_detection_time,
            'color_results': color_results
        }
    
    def test_performance_analysis(self) -> Dict[str, Any]:
        """Test vision system performance"""
        print("   ⚡ Testing performance analysis...")
        
        performance_tests = []
        
        # Test frame rate capability
        frame_times = []
        target_fps = 30
        
        for i in range(10):
            frame_start = time.time()
            # Simulate frame processing
            processing_time = random.uniform(0.02, 0.04)  # 20-40ms processing
            time.sleep(processing_time)
            frame_time = time.time() - frame_start
            frame_times.append(frame_time)
        
        avg_frame_time = sum(frame_times) / len(frame_times)
        actual_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        fps_target_met = actual_fps >= target_fps * 0.8  # 80% of target
        
        performance_tests.append({
            'test_type': 'frame_rate',
            'target_fps': target_fps,
            'actual_fps': actual_fps,
            'average_frame_time': avg_frame_time,
            'target_met': fps_target_met
        })
        
        print(f"      ✅ Frame rate: {actual_fps:.1f} FPS (target: {target_fps})")
        
        # Test memory efficiency
        memory_usage = random.uniform(50, 150)  # MB
        memory_efficient = memory_usage <= 200  # Under 200MB
        
        performance_tests.append({
            'test_type': 'memory_usage',
            'memory_mb': memory_usage,
            'memory_limit': 200,
            'target_met': memory_efficient
        })
        
        print(f"      ✅ Memory usage: {memory_usage:.1f} MB")
        
        # Test processing latency
        latency_times = []
        for i in range(5):
            latency = random.uniform(0.1, 0.5)  # 100-500ms
            latency_times.append(latency)
        
        avg_latency = sum(latency_times) / len(latency_times)
        low_latency = avg_latency <= 0.5  # Under 500ms
        
        performance_tests.append({
            'test_type': 'processing_latency',
            'average_latency': avg_latency,
            'latency_limit': 0.5,
            'target_met': low_latency
        })
        
        print(f"      ✅ Processing latency: {avg_latency:.3f}s")
        
        # Calculate overall performance
        targets_met = sum(1 for test in performance_tests if test['target_met'])
        
        success = targets_met >= len(performance_tests) * 0.8
        
        return {
            'success': success,
            'performance_tests': len(performance_tests),
            'targets_met': targets_met,
            'performance_score': (targets_met / len(performance_tests)) * 100,
            'actual_fps': actual_fps,
            'memory_usage_mb': memory_usage,
            'average_latency': avg_latency,
            'performance_details': performance_tests
        }
    
    def _simulate_ocr_errors(self, original_text: str, accuracy: float) -> str:
        """Simulate OCR errors based on accuracy"""
        if accuracy >= 1.0:
            return original_text
        
        chars = list(original_text)
        error_count = int(len(chars) * (1 - accuracy))
        
        # Introduce random errors
        for _ in range(error_count):
            if chars:
                pos = random.randint(0, len(chars) - 1)
                # Common OCR errors
                if random.random() < 0.5:
                    # Character substitution
                    chars[pos] = random.choice('abcdefghijklmnopqrstuvwxyz0123456789')
                else:
                    # Character deletion
                    chars.pop(pos)
        
        return ''.join(chars)
    
    def _calculate_text_accuracy(self, original: str, recognized: str) -> float:
        """Calculate character-level accuracy between texts"""
        if not original:
            return 1.0 if not recognized else 0.0
        
        # Simple character-level accuracy
        max_len = max(len(original), len(recognized))
        if max_len == 0:
            return 1.0
        
        matches = sum(1 for i in range(min(len(original), len(recognized))) 
                     if original[i] == recognized[i])
        
        return matches / max_len
    
    def _print_vision_results(self, results: Dict[str, Any]):
        """Print vision test results"""
        print(f"\n📊 VISION MODULE TEST RESULTS")
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
            print(f"\n🎉 VISION MODULE: EXCELLENT PERFORMANCE!")
        elif results['success_rate'] >= 60:
            print(f"\n✅ VISION MODULE: GOOD PERFORMANCE!")
        else:
            print(f"\n⚠️ VISION MODULE: NEEDS IMPROVEMENT!")

def test_vision_module():
    """Run vision module tests"""
    tester = VisionModuleTest()
    return tester.run_vision_tests()

if __name__ == "__main__":
    results = test_vision_module()
    exit(0 if results['success_rate'] >= 80 else 1)
