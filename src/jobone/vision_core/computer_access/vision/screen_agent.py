#!/usr/bin/env python3
"""
Screen Agent - Main screen monitoring and analysis agent
Integrates existing Orion Vision Core capabilities for autonomous computer access
"""

import logging
import time
import threading
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# Import vision components
from . import (
    CORE_VISION_AVAILABLE, 
    GAMING_VISION_AVAILABLE,
    create_integrated_vision_system,
    vision_metrics,
    PERFORMANCE_TARGETS
)

class AnalysisMode(Enum):
    """Screen analysis modes"""
    REAL_TIME = "real_time"
    ON_DEMAND = "on_demand"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"

class DetectionType(Enum):
    """Types of visual detection"""
    UI_ELEMENTS = "ui_elements"
    TEXT_OCR = "text_ocr"
    OBJECTS = "objects"
    COLORS = "colors"
    TEMPLATES = "templates"
    CHANGES = "changes"

@dataclass
class ScreenRegion:
    """Screen region definition"""
    x: int
    y: int
    width: int
    height: int
    name: str = ""

@dataclass
class VisualElement:
    """Detected visual element"""
    element_type: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    text: str = ""
    properties: Dict[str, Any] = None

@dataclass
class ScreenAnalysis:
    """Complete screen analysis result"""
    timestamp: float
    screen_size: Tuple[int, int]
    elements: List[VisualElement]
    text_content: str
    analysis_time: float
    confidence: float

class ScreenAgent:
    """
    Main screen monitoring and analysis agent
    Integrates existing Orion Vision Core capabilities
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.computer_access.vision.screen_agent')
        self.initialized = False
        
        # Vision system integration
        self.vision_system = None
        self.vision_type = None
        
        # Analysis configuration
        self.analysis_mode = AnalysisMode.ON_DEMAND
        self.target_fps = 30
        self.detection_types = [DetectionType.UI_ELEMENTS, DetectionType.TEXT_OCR]
        
        # Screen monitoring
        self.monitoring_active = False
        self.monitoring_thread = None
        self.last_analysis = None
        
        # Performance tracking
        self.analyses_performed = 0
        self.successful_analyses = 0
        self.failed_analyses = 0
        
        # Caching
        self.cache_enabled = True
        self.cache_duration = 1.0  # seconds
        self.cached_analysis = None
        self.cache_timestamp = 0
        
        # Thread safety
        self.analysis_lock = threading.Lock()
        
        self.logger.info("👁️ ScreenAgent initialized")
    
    def initialize(self) -> bool:
        """
        Initialize screen agent with integrated vision system
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing screen agent...")
            
            # Create integrated vision system
            self.vision_system = create_integrated_vision_system()
            self.vision_type = self.vision_system['type']
            
            self.logger.info(f"🔧 Vision system type: {self.vision_type}")
            self.logger.info(f"⚡ Capabilities: {self.vision_system['capabilities']}")
            
            # Initialize vision components based on type
            if self.vision_type == 'gaming_optimized':
                # Gaming vision system is already initialized
                self.logger.info("🎮 Gaming-optimized vision system ready")
                
            elif self.vision_type == 'core_vision':
                # Core vision functions are ready to use
                self.logger.info("🔧 Core vision system ready")
            
            self.initialized = True
            self.logger.info("✅ Screen agent initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Screen agent initialization failed: {e}")
            return False
    
    def capture_and_analyze(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture screen and perform analysis
        
        Args:
            parameters: Analysis parameters
            
        Returns:
            Dict containing analysis result
        """
        if not self.initialized:
            raise RuntimeError("Screen agent not initialized")
        
        # Check cache first
        if self.cache_enabled and self._is_cache_valid():
            self.logger.debug("📋 Using cached analysis")
            return self._format_cached_result()
        
        start_time = time.time()
        
        with self.analysis_lock:
            try:
                # Extract parameters
                region = parameters.get('region')  # Optional screen region
                detection_types = parameters.get('detection_types', self.detection_types)
                confidence_threshold = parameters.get('confidence_threshold', 0.7)
                
                self.logger.info("📸 Capturing and analyzing screen...")
                
                # Capture screen
                screen_data = self._capture_screen(region)
                
                # Perform analysis
                analysis_result = self._analyze_screen(
                    screen_data, 
                    detection_types, 
                    confidence_threshold
                )
                
                execution_time = time.time() - start_time
                
                # Update metrics
                vision_metrics.record_analysis(execution_time)
                self.analyses_performed += 1
                self.successful_analyses += 1
                
                # Cache result
                if self.cache_enabled:
                    self.cached_analysis = analysis_result
                    self.cache_timestamp = time.time()
                
                self.last_analysis = analysis_result
                
                result = {
                    'success': True,
                    'analysis': analysis_result,
                    'execution_time': execution_time,
                    'vision_type': self.vision_type,
                    'cached': False
                }
                
                self.logger.info(f"✅ Screen analysis completed ({execution_time:.3f}s)")
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                self.failed_analyses += 1
                vision_metrics.record_error()
                
                self.logger.error(f"❌ Screen analysis failed: {e}")
                
                return {
                    'success': False,
                    'error': str(e),
                    'execution_time': execution_time,
                    'vision_type': self.vision_type
                }
    
    def _capture_screen(self, region: Optional[ScreenRegion] = None) -> np.ndarray:
        """Capture screen using integrated vision system"""
        capture_start = time.time()
        
        try:
            if self.vision_type == 'gaming_optimized':
                # Use gaming vision capture
                capture_engine = self.vision_system['capture_engine']
                if region:
                    screen = capture_engine.capture_region(
                        region.x, region.y, region.width, region.height
                    )
                else:
                    screen = capture_engine.capture_screen()
                    
            elif self.vision_type == 'core_vision':
                # Use core vision capture
                capture_function = self.vision_system['capture_function']
                if region:
                    region_tuple = (region.x, region.y, region.width, region.height)
                    screen = capture_function(region_tuple)
                else:
                    screen = capture_function()
            
            else:
                raise RuntimeError(f"Unknown vision type: {self.vision_type}")
            
            capture_time = time.time() - capture_start
            vision_metrics.record_capture(capture_time)
            
            self.logger.debug(f"📸 Screen captured ({capture_time:.3f}s)")
            return screen
            
        except Exception as e:
            raise RuntimeError(f"Screen capture failed: {e}")
    
    def _analyze_screen(self, screen: np.ndarray, detection_types: List[DetectionType], 
                       confidence_threshold: float) -> ScreenAnalysis:
        """Analyze captured screen"""
        elements = []
        text_content = ""
        total_confidence = 0.0
        confidence_count = 0
        
        # UI Elements Detection
        if DetectionType.UI_ELEMENTS in detection_types:
            ui_elements = self._detect_ui_elements(screen, confidence_threshold)
            elements.extend(ui_elements)
            
        # OCR Text Detection
        if DetectionType.TEXT_OCR in detection_types:
            text_elements, extracted_text = self._perform_ocr(screen, confidence_threshold)
            elements.extend(text_elements)
            text_content = extracted_text
            
        # Object Detection (if gaming vision available)
        if DetectionType.OBJECTS in detection_types and self.vision_type == 'gaming_optimized':
            object_elements = self._detect_objects(screen, confidence_threshold)
            elements.extend(object_elements)
            
        # Color Detection
        if DetectionType.COLORS in detection_types:
            color_elements = self._detect_colors(screen, confidence_threshold)
            elements.extend(color_elements)
        
        # Calculate overall confidence
        if elements:
            total_confidence = sum(elem.confidence for elem in elements)
            confidence_count = len(elements)
            overall_confidence = total_confidence / confidence_count
        else:
            overall_confidence = 0.0
        
        return ScreenAnalysis(
            timestamp=time.time(),
            screen_size=(screen.shape[1], screen.shape[0]),
            elements=elements,
            text_content=text_content,
            analysis_time=time.time(),
            confidence=overall_confidence
        )
    
    def _detect_ui_elements(self, screen: np.ndarray, threshold: float) -> List[VisualElement]:
        """Detect UI elements using integrated vision system"""
        detection_start = time.time()
        elements = []
        
        try:
            if self.vision_type == 'gaming_optimized':
                # Use gaming vision detection
                vision_engine = self.vision_system['vision_engine']
                detections = vision_engine.analyze_screen(screen)
                
                for detection in detections:
                    if detection.confidence >= threshold:
                        element = VisualElement(
                            element_type=detection.object_type,
                            confidence=detection.confidence,
                            bbox=(detection.x, detection.y, detection.width, detection.height),
                            properties={'source': 'gaming_vision'}
                        )
                        elements.append(element)
                        
            elif self.vision_type == 'core_vision':
                # Use core vision template matching (simplified)
                # This would need template files for proper implementation
                pass
            
            detection_time = time.time() - detection_start
            vision_metrics.record_detection(detection_time)
            
            self.logger.debug(f"🔍 UI elements detected: {len(elements)} ({detection_time:.3f}s)")
            
        except Exception as e:
            self.logger.error(f"❌ UI element detection failed: {e}")
        
        return elements
    
    def _perform_ocr(self, screen: np.ndarray, threshold: float) -> Tuple[List[VisualElement], str]:
        """Perform OCR using integrated vision system"""
        ocr_start = time.time()
        elements = []
        text_content = ""
        
        try:
            if self.vision_type == 'gaming_optimized':
                # Use advanced OCR
                ocr_processor = self.vision_system['ocr_processor']
                ocr_results = ocr_processor.process_image(screen)
                
                for result in ocr_results:
                    if result.confidence >= threshold:
                        element = VisualElement(
                            element_type="text",
                            confidence=result.confidence,
                            bbox=result.bbox,
                            text=result.text,
                            properties={'source': 'advanced_ocr'}
                        )
                        elements.append(element)
                        text_content += result.text + " "
                        
            elif self.vision_type == 'core_vision':
                # Use core OCR
                ocr_function = self.vision_system['ocr_function']
                text_content = ocr_function(screen)
                
                # Create single text element (simplified)
                if text_content.strip():
                    element = VisualElement(
                        element_type="text",
                        confidence=0.8,  # Default confidence
                        bbox=(0, 0, screen.shape[1], screen.shape[0]),
                        text=text_content.strip(),
                        properties={'source': 'core_ocr'}
                    )
                    elements.append(element)
            
            ocr_time = time.time() - ocr_start
            vision_metrics.record_ocr(ocr_time)
            
            self.logger.debug(f"📝 OCR completed: {len(text_content)} chars ({ocr_time:.3f}s)")
            
        except Exception as e:
            self.logger.error(f"❌ OCR processing failed: {e}")
        
        return elements, text_content.strip()
    
    def _detect_objects(self, screen: np.ndarray, threshold: float) -> List[VisualElement]:
        """Detect objects using YOLO (gaming vision only)"""
        if self.vision_type != 'gaming_optimized':
            return []
        
        elements = []
        
        try:
            vision_engine = self.vision_system['vision_engine']
            # This would use YOLO detection from gaming vision
            # Implementation depends on gaming vision API
            
        except Exception as e:
            self.logger.error(f"❌ Object detection failed: {e}")
        
        return elements
    
    def _detect_colors(self, screen: np.ndarray, threshold: float) -> List[VisualElement]:
        """Detect specific colors (health bars, indicators, etc.)"""
        elements = []
        
        try:
            # Simple color detection implementation
            # This could be enhanced with more sophisticated color analysis
            pass
            
        except Exception as e:
            self.logger.error(f"❌ Color detection failed: {e}")
        
        return elements
    
    def _is_cache_valid(self) -> bool:
        """Check if cached analysis is still valid"""
        if not self.cached_analysis:
            return False
        
        return (time.time() - self.cache_timestamp) < self.cache_duration
    
    def _format_cached_result(self) -> Dict[str, Any]:
        """Format cached analysis result"""
        return {
            'success': True,
            'analysis': self.cached_analysis,
            'execution_time': 0.0,
            'vision_type': self.vision_type,
            'cached': True
        }
    
    def start_monitoring(self, fps: int = 30) -> bool:
        """Start continuous screen monitoring"""
        if self.monitoring_active:
            self.logger.warning("⚠️ Monitoring already active")
            return False
        
        self.target_fps = fps
        self.monitoring_active = True
        
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.logger.info(f"📹 Screen monitoring started ({fps} FPS)")
        return True
    
    def stop_monitoring(self) -> bool:
        """Stop continuous screen monitoring"""
        if not self.monitoring_active:
            return False
        
        self.monitoring_active = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        self.logger.info("🛑 Screen monitoring stopped")
        return True
    
    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        frame_time = 1.0 / self.target_fps
        
        while self.monitoring_active:
            try:
                start_time = time.time()
                
                # Perform analysis
                result = self.capture_and_analyze({})
                
                # Calculate sleep time to maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_time - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                self.logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(0.1)  # Brief pause on error
    
    def is_ready(self) -> bool:
        """Check if screen agent is ready"""
        return self.initialized and self.vision_system is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get screen agent status"""
        return {
            'initialized': self.initialized,
            'vision_type': self.vision_type,
            'monitoring_active': self.monitoring_active,
            'target_fps': self.target_fps,
            'analyses_performed': self.analyses_performed,
            'successful_analyses': self.successful_analyses,
            'failed_analyses': self.failed_analyses,
            'success_rate': (self.successful_analyses / max(self.analyses_performed, 1)) * 100,
            'cache_enabled': self.cache_enabled,
            'last_analysis_time': self.last_analysis.timestamp if self.last_analysis else None,
            'vision_capabilities': self.vision_system['capabilities'] if self.vision_system else [],
            'performance_metrics': vision_metrics.get_performance_summary()
        }
    
    def shutdown(self):
        """Shutdown screen agent"""
        self.logger.info("🛑 Shutting down screen agent")
        
        # Stop monitoring
        self.stop_monitoring()
        
        self.initialized = False
        self.logger.info("✅ Screen agent shutdown complete")
