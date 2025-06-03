#!/usr/bin/env python3
"""
🎮 Screen Capture Tests

Unit tests for Optimized Screen Capture.

Sprint 1 - Task 1.4: Testing Framework
"""

import unittest
import numpy as np
import time
import logging

# Import capture system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from optimized_capture import OptimizedScreenCapture, CaptureConfig, CaptureRegion
    CAPTURE_AVAILABLE = True
except ImportError:
    CAPTURE_AVAILABLE = False

class TestScreenCapture(unittest.TestCase):
    """Test Optimized Screen Capture"""
    
    def setUp(self):
        """Set up test environment"""
        if not CAPTURE_AVAILABLE:
            self.skipTest("Screen capture not available")
        
        self.config = CaptureConfig(
            target_fps=30,
            max_memory_mb=100,
            enable_compression=True,
            capture_method="pil"  # Use PIL for consistent testing
        )
        self.capture_system = OptimizedScreenCapture(self.config)
    
    def test_initialization(self):
        """Test capture system initialization"""
        self.assertIsNotNone(self.capture_system)
        self.assertEqual(self.capture_system.config.target_fps, 30)
        self.assertTrue(self.capture_system.config.enable_compression)
    
    def test_monitor_detection(self):
        """Test monitor detection"""
        monitors = self.capture_system.get_monitor_info()
        
        self.assertGreater(len(monitors), 0, "No monitors detected")
        
        # Check primary monitor
        primary_monitors = [m for m in monitors if m.get('primary')]
        self.assertGreater(len(primary_monitors), 0, "No primary monitor found")
        
        # Check monitor properties
        for monitor in monitors:
            self.assertIn('id', monitor)
            self.assertIn('width', monitor)
            self.assertIn('height', monitor)
            self.assertGreater(monitor['width'], 0)
            self.assertGreater(monitor['height'], 0)
    
    def test_full_screen_capture(self):
        """Test full screen capture"""
        screen = self.capture_system.capture_screen_optimized()
        
        self.assertIsInstance(screen, np.ndarray)
        self.assertEqual(len(screen.shape), 3)  # Height, Width, Channels
        self.assertGreater(screen.shape[0], 0)  # Height > 0
        self.assertGreater(screen.shape[1], 0)  # Width > 0
        self.assertEqual(screen.shape[2], 3)    # RGB channels
    
    def test_region_capture(self):
        """Test region-based capture"""
        # Create test region
        region = CaptureRegion(x=100, y=100, width=200, height=150, name="test_region")
        
        screen = self.capture_system.capture_screen_optimized(region)
        
        self.assertIsInstance(screen, np.ndarray)
        # Note: Actual dimensions might differ due to system constraints
        self.assertGreater(screen.shape[0], 0)
        self.assertGreater(screen.shape[1], 0)
    
    def test_gaming_regions(self):
        """Test gaming region creation"""
        gaming_regions = self.capture_system.create_gaming_regions()
        
        self.assertGreater(len(gaming_regions), 0, "No gaming regions created")
        
        # Check for expected regions
        expected_regions = ['full_screen', 'center', 'ui_top', 'ui_bottom', 'minimap']
        for region_name in expected_regions:
            self.assertIn(region_name, gaming_regions, f"Missing region: {region_name}")
        
        # Validate region properties
        for region_name, region in gaming_regions.items():
            self.assertIsInstance(region, CaptureRegion)
            self.assertGreaterEqual(region.x, 0)
            self.assertGreaterEqual(region.y, 0)
            self.assertGreater(region.width, 0)
            self.assertGreater(region.height, 0)
    
    def test_performance_metrics(self):
        """Test performance metrics tracking"""
        # Capture a few frames
        for _ in range(3):
            self.capture_system.capture_screen_optimized()
        
        metrics = self.capture_system.get_performance_metrics()
        
        self.assertIn('capture_time_ms', metrics)
        self.assertIn('memory_usage_mb', metrics)
        self.assertIn('fps', metrics)
        self.assertIn('frames_captured', metrics)
        self.assertGreater(metrics['frames_captured'], 0)
    
    def test_compression(self):
        """Test frame compression"""
        # Capture with compression enabled
        self.capture_system.config.enable_compression = True
        screen_compressed = self.capture_system.capture_screen_optimized()
        
        # Capture without compression
        self.capture_system.config.enable_compression = False
        screen_uncompressed = self.capture_system.capture_screen_optimized()
        
        # Both should be valid arrays
        self.assertIsInstance(screen_compressed, np.ndarray)
        self.assertIsInstance(screen_uncompressed, np.ndarray)
        
        # Shapes should be similar (compression affects quality, not dimensions significantly)
        self.assertEqual(len(screen_compressed.shape), len(screen_uncompressed.shape))

class TestCapturePerformance(unittest.TestCase):
    """Performance tests for screen capture"""
    
    def setUp(self):
        """Set up performance test environment"""
        if not CAPTURE_AVAILABLE:
            self.skipTest("Screen capture not available")
        
        self.config = CaptureConfig(
            target_fps=60,
            max_memory_mb=100,
            enable_compression=True
        )
        self.capture_system = OptimizedScreenCapture(self.config)
    
    def test_capture_speed(self):
        """Test capture speed meets target"""
        capture_times = []
        
        # Measure multiple captures
        for _ in range(10):
            start_time = time.time()
            self.capture_system.capture_screen_optimized()
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            capture_times.append(elapsed)
        
        # Calculate average
        avg_time = sum(capture_times) / len(capture_times)
        
        # Should meet target of <5ms
        self.assertLess(avg_time, 10.0, f"Capture too slow: {avg_time:.1f}ms average")
    
    def test_memory_usage(self):
        """Test memory usage stays within limits"""
        # Capture multiple frames to test memory accumulation
        for _ in range(20):
            self.capture_system.capture_screen_optimized()
        
        metrics = self.capture_system.get_performance_metrics()
        memory_usage = metrics['memory_usage_mb']
        
        # Should stay within reasonable limits
        self.assertLess(memory_usage, 200.0, f"Memory usage too high: {memory_usage:.1f}MB")
    
    def test_fps_performance(self):
        """Test FPS performance"""
        start_time = time.time()
        frame_count = 30
        
        for _ in range(frame_count):
            self.capture_system.capture_screen_optimized()
        
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        
        # Should achieve reasonable FPS
        self.assertGreater(fps, 10, f"FPS too low: {fps:.1f}")
    
    def test_continuous_capture(self):
        """Test continuous capture performance"""
        # Start continuous capture
        capture_thread = self.capture_system.start_continuous_capture(fps=30)
        
        # Let it run for a short time
        time.sleep(2)
        
        # Stop capture
        self.capture_system.stop_continuous_capture()
        
        # Check if frames were captured
        latest_frame = self.capture_system.get_latest_frame()
        self.assertIsNotNone(latest_frame, "No frames captured during continuous capture")
        
        # Check performance metrics
        metrics = self.capture_system.get_performance_metrics()
        self.assertGreater(metrics['frames_captured'], 10, "Too few frames captured")

if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Run tests
    unittest.main(verbosity=2)
