#!/usr/bin/env python3
"""
🎮 Vision Engine Tests

Unit tests for Enhanced Vision Engine V2.

Sprint 1 - Task 1.4: Testing Framework
"""

import unittest
import numpy as np
import cv2
import time
import logging
from unittest.mock import Mock, patch

# Import vision engine
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from vision_engine_v2 import EnhancedVisionEngine, VisionConfig, DetectionResult
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

class TestVisionEngine(unittest.TestCase):
    """Test Enhanced Vision Engine"""
    
    def setUp(self):
        """Set up test environment"""
        if not VISION_AVAILABLE:
            self.skipTest("Vision engine not available")
        
        self.config = VisionConfig(
            target_fps=30,
            detection_threshold=0.7,
            enable_yolo=False,  # Disable for testing
            enable_ocr=False,   # Disable for testing
            enable_color_detection=True
        )
        self.vision_engine = EnhancedVisionEngine(self.config)
    
    def test_initialization(self):
        """Test vision engine initialization"""
        self.assertIsNotNone(self.vision_engine)
        self.assertEqual(self.vision_engine.config.target_fps, 30)
        self.assertFalse(self.vision_engine.config.enable_yolo)
    
    def test_screen_capture(self):
        """Test optimized screen capture"""
        screen = self.vision_engine.capture_screen_optimized()
        
        self.assertIsInstance(screen, np.ndarray)
        self.assertEqual(len(screen.shape), 3)  # Height, Width, Channels
        self.assertGreater(screen.shape[0], 0)  # Height > 0
        self.assertGreater(screen.shape[1], 0)  # Width > 0
    
    def test_button_detection(self):
        """Test button detection"""
        # Create test image with button-like shapes
        test_image = np.ones((200, 300, 3), dtype=np.uint8) * 255
        
        # Draw button-like rectangles
        cv2.rectangle(test_image, (50, 50), (150, 80), (200, 200, 200), -1)
        cv2.rectangle(test_image, (50, 50), (150, 80), (0, 0, 0), 2)
        
        detections = self.vision_engine.detect_gaming_elements(test_image)
        
        # Should detect at least one button-like element
        button_detections = [d for d in detections if d.element_type == 'button']
        self.assertGreater(len(button_detections), 0)
    
    def test_color_detection(self):
        """Test color-based detection"""
        # Create test image with colored rectangles
        test_image = np.ones((200, 300, 3), dtype=np.uint8) * 255
        
        # Draw red rectangle (health bar)
        cv2.rectangle(test_image, (50, 50), (200, 70), (0, 0, 255), -1)
        
        # Draw green rectangle (health bar)
        cv2.rectangle(test_image, (50, 100), (180, 120), (0, 255, 0), -1)
        
        detections = self.vision_engine.detect_gaming_elements(test_image)
        
        # Should detect colored elements
        color_detections = [d for d in detections if d.element_type.startswith('color_')]
        self.assertGreater(len(color_detections), 0)
    
    def test_performance_metrics(self):
        """Test performance metrics tracking"""
        # Capture a few frames
        for _ in range(3):
            self.vision_engine.capture_screen_optimized()
        
        metrics = self.vision_engine.get_performance_metrics()
        
        self.assertIn('frames_processed', metrics)
        self.assertIn('average_fps', metrics)
        self.assertGreater(metrics['frames_processed'], 0)
    
    def test_detection_filtering(self):
        """Test detection filtering and deduplication"""
        # Create overlapping detections
        detections = [
            DetectionResult('button', (50, 50, 100, 30), (100, 65), 0.9, {}, time.time()),
            DetectionResult('button', (55, 55, 100, 30), (105, 70), 0.8, {}, time.time()),
            DetectionResult('text', (200, 200, 50, 20), (225, 210), 0.7, {}, time.time())
        ]
        
        filtered = self.vision_engine._filter_detections(detections)
        
        # Should remove overlapping detections
        self.assertLessEqual(len(filtered), len(detections))
    
    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'vision_engine'):
            # Reset performance metrics
            self.vision_engine.reset_performance_metrics()

class TestVisionPerformance(unittest.TestCase):
    """Performance tests for vision engine"""
    
    def setUp(self):
        """Set up performance test environment"""
        if not VISION_AVAILABLE:
            self.skipTest("Vision engine not available")
        
        self.config = VisionConfig(target_fps=60, enable_yolo=False)
        self.vision_engine = EnhancedVisionEngine(self.config)
    
    def test_fps_performance(self):
        """Test FPS performance target"""
        start_time = time.time()
        frame_count = 30
        
        for _ in range(frame_count):
            self.vision_engine.capture_screen_optimized()
        
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        
        # Should achieve at least 30 FPS
        self.assertGreater(fps, 30, f"FPS too low: {fps:.1f}")
    
    def test_detection_speed(self):
        """Test detection speed"""
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        start_time = time.time()
        detections = self.vision_engine.detect_gaming_elements(test_image)
        elapsed = time.time() - start_time
        
        # Should complete detection in reasonable time
        self.assertLess(elapsed, 0.1, f"Detection too slow: {elapsed:.3f}s")

if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2)
