#!/usr/bin/env python3
"""
Analysis Pipeline - Integrated vision analysis workflow
"""

import logging
import time
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .capture_engine import CaptureEngine, CaptureConfig
from .ocr_processor import OCRProcessor, OCRConfig
from .visual_detector import VisualDetector, DetectionConfig

class PipelineMode(Enum):
    """Analysis pipeline modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"

@dataclass
class PipelineConfig:
    """Analysis pipeline configuration"""
    mode: PipelineMode = PipelineMode.ADAPTIVE
    enable_capture: bool = True
    enable_ocr: bool = True
    enable_detection: bool = True
    cache_results: bool = True
    max_workers: int = 3

@dataclass
class PipelineResult:
    """Complete pipeline analysis result"""
    timestamp: float
    success: bool
    capture_result: Optional[Any] = None
    ocr_results: Optional[List] = None
    detection_results: Optional[List] = None
    processing_time: float = 0.0
    error: Optional[str] = None

class AnalysisPipeline:
    """
    Integrated vision analysis pipeline
    Coordinates capture, OCR, and detection processes
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.logger = logging.getLogger('orion.computer_access.vision.pipeline')
        
        # Configuration
        self.config = config or PipelineConfig()
        
        # Component instances
        self.capture_engine = None
        self.ocr_processor = None
        self.visual_detector = None
        
        # Pipeline state
        self.initialized = False
        self.processing_active = False
        
        # Performance tracking
        self.analyses_completed = 0
        self.successful_analyses = 0
        self.failed_analyses = 0
        self.total_processing_time = 0.0
        
        # Threading
        self.thread_pool = None
        self.pipeline_lock = threading.Lock()
        
        # Caching
        self.result_cache = {}
        self.cache_lock = threading.Lock()
        
        self.logger.info("🔄 AnalysisPipeline initialized")
    
    def initialize(self, capture_config: Optional[CaptureConfig] = None,
                  ocr_config: Optional[OCRConfig] = None,
                  detection_config: Optional[DetectionConfig] = None) -> bool:
        """
        Initialize analysis pipeline components
        
        Args:
            capture_config: Capture engine configuration
            ocr_config: OCR processor configuration
            detection_config: Visual detector configuration
            
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing analysis pipeline...")
            
            # Initialize components based on configuration
            if self.config.enable_capture:
                self.capture_engine = CaptureEngine(capture_config)
                if not self.capture_engine.initialize():
                    raise RuntimeError("Failed to initialize capture engine")
            
            if self.config.enable_ocr:
                self.ocr_processor = OCRProcessor(ocr_config)
                if not self.ocr_processor.initialize():
                    raise RuntimeError("Failed to initialize OCR processor")
            
            if self.config.enable_detection:
                self.visual_detector = VisualDetector(detection_config)
                if not self.visual_detector.initialize():
                    raise RuntimeError("Failed to initialize visual detector")
            
            # Initialize thread pool for parallel processing
            if self.config.mode == PipelineMode.PARALLEL:
                import concurrent.futures
                self.thread_pool = concurrent.futures.ThreadPoolExecutor(
                    max_workers=self.config.max_workers
                )
            
            self.initialized = True
            self.logger.info("✅ Analysis pipeline initialized successfully")
            self.logger.info(f"🔧 Mode: {self.config.mode.value}")
            self.logger.info(f"⚙️ Components: Capture={self.config.enable_capture}, "
                           f"OCR={self.config.enable_ocr}, Detection={self.config.enable_detection}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Analysis pipeline initialization failed: {e}")
            return False
    
    def analyze(self, parameters: Dict[str, Any]) -> PipelineResult:
        """
        Execute complete analysis pipeline
        
        Args:
            parameters: Analysis parameters
            
        Returns:
            PipelineResult: Complete analysis result
        """
        if not self.initialized:
            raise RuntimeError("Analysis pipeline not initialized")
        
        start_time = time.time()
        
        with self.pipeline_lock:
            try:
                self.processing_active = True
                
                # Check cache first
                cache_key = self._generate_cache_key(parameters)
                if self.config.cache_results and cache_key in self.result_cache:
                    cached_result = self.result_cache[cache_key]
                    if self._is_cache_valid(cached_result):
                        self.logger.debug("📋 Using cached analysis result")
                        return cached_result
                
                self.logger.info("🔄 Starting analysis pipeline...")
                
                # Execute pipeline based on mode
                if self.config.mode == PipelineMode.SEQUENTIAL:
                    result = self._execute_sequential(parameters)
                elif self.config.mode == PipelineMode.PARALLEL:
                    result = self._execute_parallel(parameters)
                elif self.config.mode == PipelineMode.ADAPTIVE:
                    result = self._execute_adaptive(parameters)
                else:
                    raise ValueError(f"Unknown pipeline mode: {self.config.mode}")
                
                # Update performance metrics
                processing_time = time.time() - start_time
                result.processing_time = processing_time
                
                self.analyses_completed += 1
                if result.success:
                    self.successful_analyses += 1
                else:
                    self.failed_analyses += 1
                
                self.total_processing_time += processing_time
                
                # Cache result
                if self.config.cache_results and result.success:
                    with self.cache_lock:
                        self.result_cache[cache_key] = result
                
                self.logger.info(f"✅ Analysis pipeline completed ({processing_time:.3f}s)")
                return result
                
            except Exception as e:
                processing_time = time.time() - start_time
                
                result = PipelineResult(
                    timestamp=time.time(),
                    success=False,
                    processing_time=processing_time,
                    error=str(e)
                )
                
                self.failed_analyses += 1
                self.logger.error(f"❌ Analysis pipeline failed: {e}")
                
                return result
                
            finally:
                self.processing_active = False
    
    def _execute_sequential(self, parameters: Dict[str, Any]) -> PipelineResult:
        """Execute pipeline sequentially"""
        result = PipelineResult(timestamp=time.time(), success=True)
        
        # Step 1: Capture screen
        if self.config.enable_capture:
            image = self._capture_screen(parameters)
            result.capture_result = image
        else:
            image = parameters.get('image')
            if image is None:
                raise ValueError("Image required when capture is disabled")
        
        # Step 2: OCR processing
        if self.config.enable_ocr and self.ocr_processor:
            ocr_results = self.ocr_processor.process_image(image)
            result.ocr_results = ocr_results
        
        # Step 3: Visual detection
        if self.config.enable_detection and self.visual_detector:
            detection_results = self.visual_detector.detect_elements(
                image, 
                parameters.get('element_types')
            )
            result.detection_results = detection_results
        
        return result
    
    def _execute_parallel(self, parameters: Dict[str, Any]) -> PipelineResult:
        """Execute pipeline in parallel"""
        result = PipelineResult(timestamp=time.time(), success=True)
        
        # Step 1: Capture screen (must be done first)
        if self.config.enable_capture:
            image = self._capture_screen(parameters)
            result.capture_result = image
        else:
            image = parameters.get('image')
            if image is None:
                raise ValueError("Image required when capture is disabled")
        
        # Step 2: Submit parallel tasks
        futures = []
        
        if self.config.enable_ocr and self.ocr_processor:
            future_ocr = self.thread_pool.submit(
                self.ocr_processor.process_image, image
            )
            futures.append(('ocr', future_ocr))
        
        if self.config.enable_detection and self.visual_detector:
            future_detection = self.thread_pool.submit(
                self.visual_detector.detect_elements,
                image,
                parameters.get('element_types')
            )
            futures.append(('detection', future_detection))
        
        # Step 3: Collect results
        for task_type, future in futures:
            try:
                task_result = future.result(timeout=30.0)  # 30 second timeout
                
                if task_type == 'ocr':
                    result.ocr_results = task_result
                elif task_type == 'detection':
                    result.detection_results = task_result
                    
            except Exception as e:
                self.logger.error(f"❌ Parallel task {task_type} failed: {e}")
                result.success = False
                result.error = f"Task {task_type} failed: {e}"
        
        return result
    
    def _execute_adaptive(self, parameters: Dict[str, Any]) -> PipelineResult:
        """Execute pipeline adaptively based on system load"""
        # For now, use sequential mode
        # In a full implementation, this would check system resources
        # and choose between sequential and parallel execution
        
        # Simple heuristic: use parallel if multiple processors available
        if self.config.enable_ocr and self.config.enable_detection:
            return self._execute_parallel(parameters)
        else:
            return self._execute_sequential(parameters)
    
    def _capture_screen(self, parameters: Dict[str, Any]):
        """Capture screen using capture engine"""
        if not self.capture_engine:
            raise RuntimeError("Capture engine not available")
        
        region = parameters.get('region')
        if region:
            return self.capture_engine.capture_region(
                region['x'], region['y'], 
                region['width'], region['height']
            )
        else:
            return self.capture_engine.capture_screen()
    
    def _generate_cache_key(self, parameters: Dict[str, Any]) -> str:
        """Generate cache key for parameters"""
        # Simple cache key based on parameters
        # In production, this would be more sophisticated
        key_parts = []
        
        if 'region' in parameters:
            region = parameters['region']
            key_parts.append(f"region_{region['x']}_{region['y']}_{region['width']}_{region['height']}")
        else:
            key_parts.append("fullscreen")
        
        if 'element_types' in parameters:
            element_types = sorted(parameters['element_types'])
            key_parts.append(f"types_{'_'.join(element_types)}")
        
        return "_".join(key_parts)
    
    def _is_cache_valid(self, cached_result: PipelineResult) -> bool:
        """Check if cached result is still valid"""
        # Cache valid for 1 second
        return (time.time() - cached_result.timestamp) < 1.0
    
    def clear_cache(self):
        """Clear result cache"""
        with self.cache_lock:
            self.result_cache.clear()
        self.logger.info("🧹 Analysis cache cleared")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get pipeline performance statistics"""
        avg_time = self.total_processing_time / max(self.analyses_completed, 1)
        success_rate = (self.successful_analyses / max(self.analyses_completed, 1)) * 100
        
        return {
            'analyses_completed': self.analyses_completed,
            'successful_analyses': self.successful_analyses,
            'failed_analyses': self.failed_analyses,
            'success_rate': success_rate,
            'total_processing_time': self.total_processing_time,
            'average_processing_time': avg_time,
            'cache_size': len(self.result_cache)
        }
    
    def is_ready(self) -> bool:
        """Check if analysis pipeline is ready"""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get analysis pipeline status"""
        component_status = {}
        
        if self.capture_engine:
            component_status['capture_engine'] = self.capture_engine.get_status()
        
        if self.ocr_processor:
            component_status['ocr_processor'] = self.ocr_processor.get_status()
        
        if self.visual_detector:
            component_status['visual_detector'] = self.visual_detector.get_status()
        
        return {
            'initialized': self.initialized,
            'processing_active': self.processing_active,
            'mode': self.config.mode.value,
            'components_enabled': {
                'capture': self.config.enable_capture,
                'ocr': self.config.enable_ocr,
                'detection': self.config.enable_detection
            },
            'components_status': component_status,
            'performance': self.get_performance_stats(),
            'cache_enabled': self.config.cache_results
        }
    
    def shutdown(self):
        """Shutdown analysis pipeline"""
        self.logger.info("🛑 Shutting down analysis pipeline")
        
        # Shutdown thread pool
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
            self.thread_pool = None
        
        # Shutdown components
        if self.capture_engine:
            self.capture_engine.shutdown()
        
        if self.ocr_processor:
            self.ocr_processor.shutdown()
        
        if self.visual_detector:
            self.visual_detector.shutdown()
        
        # Clear cache
        self.clear_cache()
        
        self.initialized = False
        self.logger.info("✅ Analysis pipeline shutdown complete")
