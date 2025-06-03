#!/usr/bin/env python3
"""
🎮 Vision Engine V2 - Enhanced Gaming AI Vision System

Advanced computer vision for gaming with YOLO integration and optimized performance.

Sprint 1 - Task 1.1: Vision Engine Enhancement
- YOLO v8 integration for object detection
- Custom gaming UI element training
- Real-time processing optimization
- 95%+ detection accuracy at 60 FPS target

Author: Nexus - Quantum AI Architect
Sprint: 1.1 - Foundation & Vision System
"""

import cv2
import numpy as np
import time
import threading
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from PIL import ImageGrab, Image
import warnings

# Enhanced vision dependencies
try:
    import ultralytics
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    warnings.warn(
        "🎮 YOLO not available. Install with: pip install ultralytics",
        ImportWarning
    )

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    warnings.warn(
        "🎮 OCR not available. Install with: pip install pytesseract",
        ImportWarning
    )

@dataclass
class DetectionResult:
    """Enhanced detection result with confidence and metadata"""
    element_type: str
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    center: Tuple[int, int]
    confidence: float
    metadata: Dict[str, Any]
    timestamp: float

@dataclass
class VisionConfig:
    """Vision system configuration"""
    target_fps: int = 60
    detection_threshold: float = 0.7
    ocr_threshold: float = 0.6
    enable_yolo: bool = True
    enable_ocr: bool = True
    enable_color_detection: bool = True
    capture_region: Optional[Tuple[int, int, int, int]] = None
    max_detections: int = 100

class EnhancedVisionEngine:
    """
    Enhanced Vision Engine V2 for Gaming AI
    
    Features:
    - YOLO v8 integration for advanced object detection
    - Optimized real-time processing (60 FPS target)
    - Custom gaming UI element recognition
    - Multi-threaded processing pipeline
    - Performance monitoring and optimization
    """
    
    def __init__(self, config: VisionConfig = None):
        self.config = config or VisionConfig()
        self.logger = logging.getLogger("EnhancedVisionEngine")
        
        # Performance metrics
        self.performance_metrics = {
            'frames_processed': 0,
            'total_processing_time': 0.0,
            'average_fps': 0.0,
            'detection_count': 0,
            'memory_usage_mb': 0.0
        }
        
        # Initialize components
        self.yolo_model = None
        self.ocr_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        
        # Threading
        self._processing_lock = threading.Lock()
        self._performance_lock = threading.Lock()
        
        # Initialize YOLO if available
        if YOLO_AVAILABLE and self.config.enable_yolo:
            self._initialize_yolo()
        
        self.logger.info("🎮 Enhanced Vision Engine V2 initialized")
    
    def _initialize_yolo(self):
        """Initialize YOLO model for object detection"""
        try:
            # Use YOLOv8 nano for speed, can upgrade to larger models for accuracy
            self.yolo_model = YOLO('yolov8n.pt')
            self.logger.info("✅ YOLO v8 model loaded successfully")
        except Exception as e:
            self.logger.error(f"❌ YOLO initialization failed: {e}")
            self.yolo_model = None
    
    def capture_screen_optimized(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Optimized screen capture with region support"""
        start_time = time.time()
        
        try:
            # Use specified region or config region
            capture_region = region or self.config.capture_region
            
            if capture_region:
                screenshot = ImageGrab.grab(bbox=capture_region)
            else:
                screenshot = ImageGrab.grab()
            
            # Convert to numpy array efficiently
            screen_array = np.array(screenshot)
            
            # Update performance metrics
            capture_time = time.time() - start_time
            self._update_performance_metrics(capture_time)
            
            return screen_array
            
        except Exception as e:
            self.logger.error(f"🎮 Screen capture failed: {e}")
            return np.zeros((100, 100, 3), dtype=np.uint8)
    
    def detect_gaming_elements(self, screen: np.ndarray) -> List[DetectionResult]:
        """Enhanced gaming element detection using multiple methods"""
        start_time = time.time()
        detections = []
        
        with self._processing_lock:
            try:
                # YOLO-based object detection
                if self.yolo_model and self.config.enable_yolo:
                    yolo_detections = self._yolo_detection(screen)
                    detections.extend(yolo_detections)
                
                # Traditional computer vision detection
                cv_detections = self._traditional_cv_detection(screen)
                detections.extend(cv_detections)
                
                # OCR-based text detection
                if OCR_AVAILABLE and self.config.enable_ocr:
                    ocr_detections = self._enhanced_ocr_detection(screen)
                    detections.extend(ocr_detections)
                
                # Color-based detection (health bars, etc.)
                if self.config.enable_color_detection:
                    color_detections = self._color_based_detection(screen)
                    detections.extend(color_detections)
                
                # Filter and sort detections
                detections = self._filter_detections(detections)
                
                # Update metrics
                processing_time = time.time() - start_time
                with self._performance_lock:
                    self.performance_metrics['detection_count'] += len(detections)
                
                self.logger.debug(f"🎮 Detected {len(detections)} elements in {processing_time:.3f}s")
                
            except Exception as e:
                self.logger.error(f"🎮 Detection failed: {e}")
        
        return detections
    
    def _yolo_detection(self, screen: np.ndarray) -> List[DetectionResult]:
        """YOLO-based object detection for gaming elements"""
        detections = []
        
        if not self.yolo_model:
            return detections
        
        try:
            # Run YOLO inference
            results = self.yolo_model(screen, conf=self.config.detection_threshold, verbose=False)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract box information
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Convert to our format
                        x, y, w, h = int(x1), int(y1), int(x2-x1), int(y2-y1)
                        center = (x + w//2, y + h//2)
                        
                        # Map YOLO classes to gaming elements
                        element_type = self._map_yolo_class_to_gaming_element(class_id)
                        
                        detection = DetectionResult(
                            element_type=element_type,
                            bbox=(x, y, w, h),
                            center=center,
                            confidence=confidence,
                            metadata={
                                'method': 'yolo',
                                'class_id': class_id,
                                'yolo_confidence': confidence
                            },
                            timestamp=time.time()
                        )
                        
                        detections.append(detection)
            
        except Exception as e:
            self.logger.error(f"🎮 YOLO detection failed: {e}")
        
        return detections
    
    def _map_yolo_class_to_gaming_element(self, class_id: int) -> str:
        """Map YOLO class IDs to gaming element types"""
        # YOLO COCO classes that might be relevant for gaming
        gaming_class_map = {
            0: 'character',      # person
            1: 'vehicle',        # bicycle -> vehicle
            2: 'vehicle',        # car -> vehicle
            3: 'vehicle',        # motorcycle -> vehicle
            5: 'vehicle',        # bus -> vehicle
            6: 'vehicle',        # train -> vehicle
            7: 'vehicle',        # truck -> vehicle
            15: 'animal',        # cat -> animal/pet
            16: 'animal',        # dog -> animal/pet
            62: 'furniture',     # chair -> furniture
            63: 'furniture',     # couch -> furniture
            67: 'furniture',     # dining table -> furniture
            72: 'screen',        # tv -> screen/monitor
            73: 'device',        # laptop -> device
            76: 'device',        # keyboard -> device
            77: 'device',        # cell phone -> device
        }
        
        return gaming_class_map.get(class_id, 'object')
    
    def _traditional_cv_detection(self, screen: np.ndarray) -> List[DetectionResult]:
        """Traditional computer vision detection for UI elements"""
        detections = []
        
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
            
            # Enhanced button detection
            button_detections = self._detect_buttons_enhanced(gray)
            detections.extend(button_detections)
            
            # Enhanced icon detection
            icon_detections = self._detect_icons_enhanced(gray)
            detections.extend(icon_detections)
            
            # Window detection
            window_detections = self._detect_windows(gray)
            detections.extend(window_detections)
            
        except Exception as e:
            self.logger.error(f"🎮 Traditional CV detection failed: {e}")
        
        return detections
    
    def _detect_buttons_enhanced(self, gray: np.ndarray) -> List[DetectionResult]:
        """Enhanced button detection using multiple techniques"""
        buttons = []
        
        try:
            # Edge detection with multiple thresholds
            edges1 = cv2.Canny(gray, 50, 150)
            edges2 = cv2.Canny(gray, 100, 200)
            edges = cv2.bitwise_or(edges1, edges2)
            
            # Morphological operations to connect edges
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by area (button size range)
                if 500 < area < 50000:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    
                    # Filter by aspect ratio (button-like shapes)
                    if 0.3 < aspect_ratio < 5.0:
                        # Calculate confidence based on shape regularity
                        hull = cv2.convexHull(contour)
                        hull_area = cv2.contourArea(hull)
                        solidity = area / hull_area if hull_area > 0 else 0
                        
                        confidence = min(0.9, solidity * 0.8 + 0.2)
                        
                        if confidence > self.config.detection_threshold:
                            button = DetectionResult(
                                element_type='button',
                                bbox=(x, y, w, h),
                                center=(x + w//2, y + h//2),
                                confidence=confidence,
                                metadata={
                                    'method': 'cv_enhanced',
                                    'area': area,
                                    'aspect_ratio': aspect_ratio,
                                    'solidity': solidity
                                },
                                timestamp=time.time()
                            )
                            buttons.append(button)
            
        except Exception as e:
            self.logger.error(f"🎮 Enhanced button detection failed: {e}")
        
        return buttons
    
    def _detect_icons_enhanced(self, gray: np.ndarray) -> List[DetectionResult]:
        """Enhanced icon detection using template matching and feature detection"""
        icons = []
        
        try:
            # Use SIFT for feature detection (good for icons)
            sift = cv2.SIFT_create()
            keypoints, descriptors = sift.detectAndCompute(gray, None)
            
            # Group keypoints into potential icon regions
            if keypoints:
                # Convert keypoints to numpy array
                points = np.array([kp.pt for kp in keypoints])
                
                # Use clustering to group nearby keypoints
                from sklearn.cluster import DBSCAN
                
                if len(points) > 5:
                    clustering = DBSCAN(eps=30, min_samples=3).fit(points)
                    labels = clustering.labels_
                    
                    # Process each cluster as potential icon
                    for label in set(labels):
                        if label == -1:  # Noise
                            continue
                        
                        cluster_points = points[labels == label]
                        
                        # Calculate bounding box for cluster
                        x_min, y_min = cluster_points.min(axis=0)
                        x_max, y_max = cluster_points.max(axis=0)
                        
                        x, y = int(x_min), int(y_min)
                        w, h = int(x_max - x_min), int(y_max - y_min)
                        
                        # Filter by size (icon size range)
                        if 16 <= w <= 128 and 16 <= h <= 128:
                            aspect_ratio = w / h
                            
                            # Icons are usually square-ish
                            if 0.5 <= aspect_ratio <= 2.0:
                                confidence = min(0.8, len(cluster_points) / 20.0)
                                
                                icon = DetectionResult(
                                    element_type='icon',
                                    bbox=(x, y, w, h),
                                    center=(x + w//2, y + h//2),
                                    confidence=confidence,
                                    metadata={
                                        'method': 'sift_clustering',
                                        'keypoint_count': len(cluster_points),
                                        'aspect_ratio': aspect_ratio
                                    },
                                    timestamp=time.time()
                                )
                                icons.append(icon)
        
        except Exception as e:
            self.logger.error(f"🎮 Enhanced icon detection failed: {e}")
        
        return icons
    
    def _detect_windows(self, gray: np.ndarray) -> List[DetectionResult]:
        """Detect game windows and panels"""
        windows = []
        
        try:
            # Use Hough lines to detect rectangular windows
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
            
            if lines is not None:
                # Group lines into rectangles (simplified approach)
                horizontal_lines = []
                vertical_lines = []
                
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    
                    if abs(angle) < 10 or abs(angle) > 170:  # Horizontal
                        horizontal_lines.append(line[0])
                    elif 80 < abs(angle) < 100:  # Vertical
                        vertical_lines.append(line[0])
                
                # Simple window detection based on line intersections
                # (This is a simplified implementation - could be enhanced)
                if len(horizontal_lines) >= 2 and len(vertical_lines) >= 2:
                    window = DetectionResult(
                        element_type='window',
                        bbox=(50, 50, 200, 150),  # Placeholder
                        center=(150, 125),
                        confidence=0.6,
                        metadata={
                            'method': 'hough_lines',
                            'h_lines': len(horizontal_lines),
                            'v_lines': len(vertical_lines)
                        },
                        timestamp=time.time()
                    )
                    windows.append(window)
        
        except Exception as e:
            self.logger.error(f"🎮 Window detection failed: {e}")
        
        return windows
    
    def _enhanced_ocr_detection(self, screen: np.ndarray) -> List[DetectionResult]:
        """Enhanced OCR detection with preprocessing"""
        text_detections = []
        
        if not OCR_AVAILABLE:
            return text_detections
        
        try:
            # Preprocess image for better OCR
            gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
            
            # Multiple preprocessing approaches
            preprocessed_images = [
                gray,  # Original
                cv2.GaussianBlur(gray, (3, 3), 0),  # Slight blur
                cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],  # Otsu threshold
                cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)  # Adaptive
            ]
            
            for i, processed_img in enumerate(preprocessed_images):
                try:
                    # Get detailed OCR data
                    data = pytesseract.image_to_data(processed_img, config=self.ocr_config, output_type=pytesseract.Output.DICT)
                    
                    for j, text in enumerate(data['text']):
                        if text.strip() and len(text.strip()) > 1:  # Non-empty text with minimum length
                            confidence = float(data['conf'][j]) / 100.0
                            
                            if confidence > self.config.ocr_threshold:
                                x, y, w, h = data['left'][j], data['top'][j], data['width'][j], data['height'][j]
                                
                                detection = DetectionResult(
                                    element_type='text',
                                    bbox=(x, y, w, h),
                                    center=(x + w//2, y + h//2),
                                    confidence=confidence,
                                    metadata={
                                        'method': f'ocr_enhanced_{i}',
                                        'text': text.strip(),
                                        'preprocessing': i,
                                        'word_count': len(text.strip().split())
                                    },
                                    timestamp=time.time()
                                )
                                text_detections.append(detection)
                
                except Exception as e:
                    self.logger.debug(f"🎮 OCR preprocessing {i} failed: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"🎮 Enhanced OCR detection failed: {e}")
        
        return text_detections
    
    def _color_based_detection(self, screen: np.ndarray) -> List[DetectionResult]:
        """Enhanced color-based detection for health bars, etc."""
        color_detections = []
        
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(screen, cv2.COLOR_RGB2HSV)
            
            # Define enhanced color ranges
            color_ranges = {
                'health_red': [(0, 50, 50), (10, 255, 255)],
                'health_green': [(40, 50, 50), (80, 255, 255)],
                'mana_blue': [(100, 50, 50), (130, 255, 255)],
                'warning_yellow': [(20, 50, 50), (30, 255, 255)],
                'enemy_red': [(170, 50, 50), (180, 255, 255)]
            }
            
            for color_name, (lower, upper) in color_ranges.items():
                lower = np.array(lower)
                upper = np.array(upper)
                
                # Create mask
                mask = cv2.inRange(hsv, lower, upper)
                
                # Morphological operations to clean up mask
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                
                # Find contours
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    
                    # Filter by area
                    if 100 < area < 20000:
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = w / h
                        
                        # Health bars are typically wide
                        if aspect_ratio > 1.5 or color_name.endswith('_red') or color_name.endswith('_green'):
                            confidence = min(0.8, area / 10000.0)
                            
                            detection = DetectionResult(
                                element_type=f'color_{color_name}',
                                bbox=(x, y, w, h),
                                center=(x + w//2, y + h//2),
                                confidence=confidence,
                                metadata={
                                    'method': 'color_detection',
                                    'color': color_name,
                                    'area': area,
                                    'aspect_ratio': aspect_ratio
                                },
                                timestamp=time.time()
                            )
                            color_detections.append(detection)
        
        except Exception as e:
            self.logger.error(f"🎮 Color detection failed: {e}")
        
        return color_detections
    
    def _filter_detections(self, detections: List[DetectionResult]) -> List[DetectionResult]:
        """Filter and deduplicate detections"""
        if not detections:
            return detections
        
        # Sort by confidence
        detections.sort(key=lambda x: x.confidence, reverse=True)
        
        # Remove duplicates (overlapping detections)
        filtered = []
        for detection in detections:
            is_duplicate = False
            
            for existing in filtered:
                if self._calculate_overlap(detection.bbox, existing.bbox) > 0.5:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(detection)
        
        # Limit number of detections
        return filtered[:self.config.max_detections]
    
    def _calculate_overlap(self, bbox1: Tuple[int, int, int, int], bbox2: Tuple[int, int, int, int]) -> float:
        """Calculate overlap ratio between two bounding boxes"""
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # Calculate intersection
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _update_performance_metrics(self, processing_time: float):
        """Update performance metrics"""
        with self._performance_lock:
            self.performance_metrics['frames_processed'] += 1
            self.performance_metrics['total_processing_time'] += processing_time
            
            if self.performance_metrics['frames_processed'] > 0:
                avg_time = self.performance_metrics['total_processing_time'] / self.performance_metrics['frames_processed']
                self.performance_metrics['average_fps'] = 1.0 / avg_time if avg_time > 0 else 0.0
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        with self._performance_lock:
            return self.performance_metrics.copy()
    
    def reset_performance_metrics(self):
        """Reset performance metrics"""
        with self._performance_lock:
            self.performance_metrics = {
                'frames_processed': 0,
                'total_processing_time': 0.0,
                'average_fps': 0.0,
                'detection_count': 0,
                'memory_usage_mb': 0.0
            }

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎮 Enhanced Vision Engine V2 - Sprint 1 Test")
    print("=" * 60)
    
    # Create enhanced vision engine
    config = VisionConfig(
        target_fps=60,
        detection_threshold=0.7,
        enable_yolo=True,
        enable_ocr=True,
        enable_color_detection=True
    )
    
    vision_engine = EnhancedVisionEngine(config)
    
    # Test screen capture
    print("\n📸 Testing optimized screen capture...")
    screen = vision_engine.capture_screen_optimized()
    print(f"✅ Screen captured: {screen.shape}")
    
    # Test enhanced detection
    print("\n🔍 Testing enhanced gaming element detection...")
    detections = vision_engine.detect_gaming_elements(screen)
    print(f"✅ Detected {len(detections)} gaming elements")
    
    # Show detection details
    for i, detection in enumerate(detections[:5]):  # Show first 5
        print(f"   Detection {i+1}: {detection.element_type} at {detection.center} "
              f"(confidence: {detection.confidence:.2f}, method: {detection.metadata.get('method', 'unknown')})")
    
    # Performance metrics
    metrics = vision_engine.get_performance_metrics()
    print(f"\n📊 Performance Metrics:")
    print(f"   Average FPS: {metrics['average_fps']:.1f}")
    print(f"   Frames Processed: {metrics['frames_processed']}")
    print(f"   Total Detections: {metrics['detection_count']}")
    
    print("\n🎉 Sprint 1 - Task 1.1 test completed!")
    print("🎯 Target: 95%+ detection accuracy at 60 FPS")
    print(f"📈 Current: {len(detections)} detections at {metrics['average_fps']:.1f} FPS")
