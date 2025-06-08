#!/usr/bin/env python3
"""
Visual Detector - UI elements and object detection
"""

import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import detection libraries
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class DetectionMethod(Enum):
    """Visual detection methods"""
    TEMPLATE_MATCHING = "template_matching"
    COLOR_DETECTION = "color_detection"
    CONTOUR_DETECTION = "contour_detection"
    FEATURE_MATCHING = "feature_matching"

@dataclass
class Detection:
    """Visual detection result"""
    object_type: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    center: Tuple[int, int]
    method: str
    properties: Dict[str, Any] = None

@dataclass
class DetectionConfig:
    """Visual detection configuration"""
    methods: List[DetectionMethod] = None
    confidence_threshold: float = 0.7
    template_threshold: float = 0.8
    color_tolerance: int = 30
    contour_min_area: int = 100

class VisualDetector:
    """
    Visual element and object detector
    Supports multiple detection methods
    """
    
    def __init__(self, config: Optional[DetectionConfig] = None):
        self.logger = logging.getLogger('orion.computer_access.vision.detector')
        
        # Configuration
        self.config = config or DetectionConfig()
        if self.config.methods is None:
            self.config.methods = [
                DetectionMethod.TEMPLATE_MATCHING,
                DetectionMethod.COLOR_DETECTION,
                DetectionMethod.CONTOUR_DETECTION
            ]
        
        # Template storage
        self.templates = {}
        self.color_targets = {}
        
        # Performance tracking
        self.detections_performed = 0
        self.total_detection_time = 0.0
        self.last_detection_time = 0.0
        
        self.initialized = False
        
        self.logger.info("🔍 VisualDetector initialized")
    
    def initialize(self) -> bool:
        """
        Initialize visual detector
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing visual detector...")
            
            if not CV2_AVAILABLE:
                self.logger.warning("⚠️ OpenCV not available, limited functionality")
            
            # Load default UI element templates
            self._load_default_templates()
            
            # Load default color targets
            self._load_default_colors()
            
            self.initialized = True
            self.logger.info("✅ Visual detector initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Visual detector initialization failed: {e}")
            return False
    
    def detect_elements(self, image: np.ndarray, 
                       element_types: Optional[List[str]] = None) -> List[Detection]:
        """
        Detect visual elements in image
        
        Args:
            image: Input image
            element_types: Specific element types to detect (optional)
            
        Returns:
            List of detected elements
        """
        if not self.initialized:
            raise RuntimeError("Visual detector not initialized")
        
        start_time = time.time()
        detections = []
        
        try:
            # Template matching detection
            if DetectionMethod.TEMPLATE_MATCHING in self.config.methods:
                template_detections = self._detect_templates(image, element_types)
                detections.extend(template_detections)
            
            # Color-based detection
            if DetectionMethod.COLOR_DETECTION in self.config.methods:
                color_detections = self._detect_colors(image, element_types)
                detections.extend(color_detections)
            
            # Contour-based detection
            if DetectionMethod.CONTOUR_DETECTION in self.config.methods:
                contour_detections = self._detect_contours(image, element_types)
                detections.extend(contour_detections)
            
            # Feature matching (if available)
            if DetectionMethod.FEATURE_MATCHING in self.config.methods and CV2_AVAILABLE:
                feature_detections = self._detect_features(image, element_types)
                detections.extend(feature_detections)
            
            # Filter by confidence threshold
            filtered_detections = [
                detection for detection in detections
                if detection.confidence >= self.config.confidence_threshold
            ]
            
            # Remove overlapping detections
            final_detections = self._remove_overlaps(filtered_detections)
            
            # Update performance metrics
            detection_time = time.time() - start_time
            self.detections_performed += 1
            self.total_detection_time += detection_time
            self.last_detection_time = detection_time
            
            self.logger.debug(f"🔍 Detection completed: {len(final_detections)} elements ({detection_time:.3f}s)")
            return final_detections
            
        except Exception as e:
            self.logger.error(f"❌ Element detection failed: {e}")
            raise
    
    def _detect_templates(self, image: np.ndarray, 
                         element_types: Optional[List[str]]) -> List[Detection]:
        """Detect elements using template matching"""
        detections = []
        
        if not CV2_AVAILABLE:
            return detections
        
        try:
            # Convert image to grayscale for template matching
            if len(image.shape) == 3:
                gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray_image = image
            
            # Check each template
            templates_to_check = self.templates
            if element_types:
                templates_to_check = {
                    k: v for k, v in self.templates.items() 
                    if k in element_types
                }
            
            for template_name, template_data in templates_to_check.items():
                template = template_data['template']
                
                # Perform template matching
                result = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
                locations = np.where(result >= self.config.template_threshold)
                
                # Create detections for matches
                for pt in zip(*locations[::-1]):
                    x, y = pt
                    h, w = template.shape
                    confidence = result[y, x]
                    
                    detection = Detection(
                        object_type=template_name,
                        confidence=confidence,
                        bbox=(x, y, w, h),
                        center=(x + w//2, y + h//2),
                        method="template_matching",
                        properties={'template_name': template_name}
                    )
                    detections.append(detection)
                    
        except Exception as e:
            self.logger.error(f"❌ Template detection failed: {e}")
        
        return detections
    
    def _detect_colors(self, image: np.ndarray, 
                      element_types: Optional[List[str]]) -> List[Detection]:
        """Detect elements using color detection"""
        detections = []
        
        if not CV2_AVAILABLE:
            return detections
        
        try:
            # Convert to HSV for better color detection
            hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            # Check each color target
            colors_to_check = self.color_targets
            if element_types:
                colors_to_check = {
                    k: v for k, v in self.color_targets.items() 
                    if k in element_types
                }
            
            for color_name, color_data in colors_to_check.items():
                lower_bound = np.array(color_data['lower'])
                upper_bound = np.array(color_data['upper'])
                
                # Create mask for color range
                mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
                
                # Find contours in mask
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > self.config.contour_min_area:
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        # Calculate confidence based on area and shape
                        confidence = min(1.0, area / 10000.0)  # Normalize area
                        
                        detection = Detection(
                            object_type=color_name,
                            confidence=confidence,
                            bbox=(x, y, w, h),
                            center=(x + w//2, y + h//2),
                            method="color_detection",
                            properties={'color_name': color_name, 'area': area}
                        )
                        detections.append(detection)
                        
        except Exception as e:
            self.logger.error(f"❌ Color detection failed: {e}")
        
        return detections
    
    def _detect_contours(self, image: np.ndarray, 
                        element_types: Optional[List[str]]) -> List[Detection]:
        """Detect elements using contour detection"""
        detections = []
        
        if not CV2_AVAILABLE:
            return detections
        
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray_image = image
            
            # Apply edge detection
            edges = cv2.Canny(gray_image, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > self.config.contour_min_area:
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Classify shape based on contour properties
                    object_type = self._classify_contour(contour)
                    
                    # Skip if element type filtering is active and this type not requested
                    if element_types and object_type not in element_types:
                        continue
                    
                    # Calculate confidence based on contour properties
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        confidence = min(1.0, circularity)
                    else:
                        confidence = 0.5
                    
                    detection = Detection(
                        object_type=object_type,
                        confidence=confidence,
                        bbox=(x, y, w, h),
                        center=(x + w//2, y + h//2),
                        method="contour_detection",
                        properties={'area': area, 'perimeter': perimeter}
                    )
                    detections.append(detection)
                    
        except Exception as e:
            self.logger.error(f"❌ Contour detection failed: {e}")
        
        return detections
    
    def _detect_features(self, image: np.ndarray, 
                        element_types: Optional[List[str]]) -> List[Detection]:
        """Detect elements using feature matching"""
        detections = []
        
        # Feature matching implementation would go here
        # This is a placeholder for more advanced feature detection
        
        return detections
    
    def _classify_contour(self, contour) -> str:
        """Classify contour shape"""
        # Approximate contour to polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Classify based on number of vertices
        vertices = len(approx)
        
        if vertices == 3:
            return "triangle"
        elif vertices == 4:
            # Check if it's a square or rectangle
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = float(w) / h
            if 0.95 <= aspect_ratio <= 1.05:
                return "square"
            else:
                return "rectangle"
        elif vertices > 4:
            # Check if it's circular
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter * perimeter)
                if circularity > 0.7:
                    return "circle"
        
        return "unknown_shape"
    
    def _remove_overlaps(self, detections: List[Detection]) -> List[Detection]:
        """Remove overlapping detections"""
        if not detections:
            return detections
        
        # Sort by confidence (highest first)
        sorted_detections = sorted(detections, key=lambda x: x.confidence, reverse=True)
        final_detections = []
        
        for detection in sorted_detections:
            # Check if this detection overlaps significantly with any existing detection
            overlap_found = False
            
            for existing in final_detections:
                if self._calculate_overlap(detection.bbox, existing.bbox) > 0.5:
                    overlap_found = True
                    break
            
            if not overlap_found:
                final_detections.append(detection)
        
        return final_detections
    
    def _calculate_overlap(self, bbox1: Tuple[int, int, int, int], 
                          bbox2: Tuple[int, int, int, int]) -> float:
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
        
        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        
        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union_area = area1 + area2 - intersection_area
        
        if union_area == 0:
            return 0.0
        
        return intersection_area / union_area
    
    def _load_default_templates(self):
        """Load default UI element templates"""
        # This would load actual template images in a real implementation
        # For now, create placeholder templates
        if CV2_AVAILABLE:
            # Create simple button template
            button_template = np.ones((30, 100), dtype=np.uint8) * 128
            cv2.rectangle(button_template, (2, 2), (98, 28), 255, 2)
            
            self.templates['button'] = {
                'template': button_template,
                'description': 'Generic button template'
            }
            
            # Create checkbox template
            checkbox_template = np.ones((20, 20), dtype=np.uint8) * 255
            cv2.rectangle(checkbox_template, (2, 2), (18, 18), 0, 2)
            
            self.templates['checkbox'] = {
                'template': checkbox_template,
                'description': 'Checkbox template'
            }
    
    def _load_default_colors(self):
        """Load default color targets"""
        # Common UI colors in HSV format
        self.color_targets = {
            'red_button': {
                'lower': [0, 50, 50],
                'upper': [10, 255, 255],
                'description': 'Red UI elements'
            },
            'green_button': {
                'lower': [40, 50, 50],
                'upper': [80, 255, 255],
                'description': 'Green UI elements'
            },
            'blue_button': {
                'lower': [100, 50, 50],
                'upper': [130, 255, 255],
                'description': 'Blue UI elements'
            }
        }
    
    def add_template(self, name: str, template: np.ndarray, 
                    description: str = "") -> bool:
        """Add custom template"""
        try:
            self.templates[name] = {
                'template': template,
                'description': description
            }
            self.logger.info(f"🔍 Template added: {name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to add template: {e}")
            return False
    
    def add_color_target(self, name: str, lower_hsv: List[int], 
                        upper_hsv: List[int], description: str = "") -> bool:
        """Add custom color target"""
        try:
            self.color_targets[name] = {
                'lower': lower_hsv,
                'upper': upper_hsv,
                'description': description
            }
            self.logger.info(f"🎨 Color target added: {name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to add color target: {e}")
            return False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get detection performance statistics"""
        avg_time = self.total_detection_time / max(self.detections_performed, 1)
        
        return {
            'detections_performed': self.detections_performed,
            'total_detection_time': self.total_detection_time,
            'average_detection_time': avg_time,
            'last_detection_time': self.last_detection_time
        }
    
    def is_ready(self) -> bool:
        """Check if visual detector is ready"""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get visual detector status"""
        return {
            'initialized': self.initialized,
            'available_libraries': {
                'opencv': CV2_AVAILABLE,
                'pil': PIL_AVAILABLE
            },
            'templates_loaded': len(self.templates),
            'color_targets_loaded': len(self.color_targets),
            'detection_methods': [method.value for method in self.config.methods],
            'config': {
                'confidence_threshold': self.config.confidence_threshold,
                'template_threshold': self.config.template_threshold,
                'color_tolerance': self.config.color_tolerance,
                'contour_min_area': self.config.contour_min_area
            },
            'performance': self.get_performance_stats()
        }
    
    def shutdown(self):
        """Shutdown visual detector"""
        self.logger.info("🛑 Shutting down visual detector")
        
        # Clear templates and targets
        self.templates.clear()
        self.color_targets.clear()
        
        self.initialized = False
        self.logger.info("✅ Visual detector shutdown complete")
