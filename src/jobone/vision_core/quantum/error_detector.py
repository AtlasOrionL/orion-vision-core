"""
🔍 Quantum Error Detector - Q05.2.2 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Q05.2.2 Quantum Error Detection
Priority: CRITICAL - Modular Design Refactoring Phase 11
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional

# Import core components from modular design
from .modules.error_correction.error_detection_core import (
    QuantumErrorType, ErrorSeverity, DetectionMethod,
    QuantumError, DetectionResult,
    create_quantum_error, create_detection_result, classify_error_severity
)

# Import engine component
from .modules.error_correction.error_detection_engine import (
    ErrorDetectionEngine
)

# Import statistics component
from .modules.error_correction.error_detection_statistics import (
    ErrorDetectionStatistics, get_error_detection_statistics,
    create_error_detection_statistics, analyze_detection_batch,
    get_detection_summary, get_error_summary
)

# Enhanced Error Detector with statistics
class QuantumErrorDetector:
    """
    Enhanced Quantum Error Detector with integrated statistics
    
    Unified interface for quantum error detection with modular design
    """
    
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize components
        self.engine = ErrorDetectionEngine()
        self.statistics = create_error_detection_statistics()
        
        # Error management
        self.detected_errors: List[QuantumError] = []
        self.detection_results: List[DetectionResult] = []
        self.active_detections: Dict[str, QuantumError] = {}
        
        # Detection parameters
        self.detection_threshold = 0.01
        self.confidence_threshold = 0.8
        self.max_detection_time = 1.0
        
        # Performance tracking
        self.total_detections = 0
        self.successful_detections = 0
        self.false_positives = 0
        self.false_negatives = 0
        
        # ALT_LAS integration
        self.alt_las_integration_active = False
        self.consciousness_error_detection = False
        
        # Threading
        self._detection_lock = threading.Lock()
        self._error_lock = threading.Lock()
        
        # Status
        self.initialized = False
        self.active = False
        
        self.logger.info("🔍 QuantumErrorDetector initialized with modular design")
    
    def initialize(self) -> bool:
        """Initialize quantum error detector"""
        try:
            self.initialized = True
            self.active = True
            
            self.logger.info("✅ QuantumErrorDetector initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ QuantumErrorDetector initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown quantum error detector"""
        try:
            self.active = False
            
            with self._detection_lock:
                self.active_detections.clear()
            
            self.logger.info("🔴 QuantumErrorDetector shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ QuantumErrorDetector shutdown failed: {e}")
            return False
    
    def detect_error(self, quantum_state, detection_method: DetectionMethod = DetectionMethod.PARITY_CHECK,
                    qubit_index: int = 0) -> Optional[DetectionResult]:
        """Detect quantum error in state"""
        try:
            # Use engine for detection
            result = self.engine.detect_error(quantum_state, detection_method, qubit_index)
            
            if result:
                # Add to statistics
                self.statistics.add_detection_result(result)
                
                # Store result
                with self._detection_lock:
                    self.detection_results.append(result)
                    # Keep history manageable
                    if len(self.detection_results) > 1000:
                        self.detection_results = self.detection_results[-500:]
                
                # Store error if detected
                if result.error_detected and result.detected_error:
                    with self._error_lock:
                        self.detected_errors.append(result.detected_error)
                        if len(self.detected_errors) > 1000:
                            self.detected_errors = self.detected_errors[-500:]
                
                # Update counters
                self.total_detections += 1
                if result.error_detected:
                    self.successful_detections += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error detection failed: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status"""
        with self._detection_lock, self._error_lock:
            engine_stats = self.engine.get_engine_statistics()
            detection_stats = self.statistics.get_comprehensive_statistics()
            
            return {
                'initialized': self.initialized,
                'active': self.active,
                'total_detections': self.total_detections,
                'successful_detections': self.successful_detections,
                'false_positives': self.false_positives,
                'false_negatives': self.false_negatives,
                'detection_rate': (self.successful_detections / max(1, self.total_detections)) * 100,
                'detection_history_size': len(self.detection_results),
                'error_history_size': len(self.detected_errors),
                'active_detections': len(self.active_detections),
                'alt_las_integration': self.alt_las_integration_active,
                'consciousness_detection': self.consciousness_error_detection,
                'engine_statistics': engine_stats,
                'detection_statistics': detection_stats
            }
    
    def get_error_detection_statistics(self):
        """Get comprehensive error detection statistics"""
        return self.statistics.get_comprehensive_statistics()

# Utility functions
def create_quantum_error_detector(config=None) -> QuantumErrorDetector:
    """Create Quantum Error Detector system"""
    return QuantumErrorDetector(config)

def test_quantum_error_detector():
    """Test Quantum Error Detector system"""
    print("🔍 Testing Quantum Error Detector...")
    
    # Create error detector
    detector = create_quantum_error_detector()
    detector.initialize()
    print("✅ Error detector created")
    
    # Test detection methods
    methods = list(DetectionMethod)
    print(f"✅ Available methods: {[method.value for method in methods]}")
    
    # Test error types
    error_types = list(QuantumErrorType)
    print(f"✅ Supported error types: {[error_type.value for error_type in error_types]}")
    
    # Get comprehensive status
    status = detector.get_status()
    print(f"✅ Detector Status:")
    print(f"    - Total detections: {status['total_detections']}")
    print(f"    - Detection rate: {status['detection_rate']:.1f}%")
    print(f"    - ALT_LAS integration: {status['alt_las_integration']}")
    
    print("🚀 Quantum Error Detector test completed!")

# Export all components for backward compatibility
__all__ = [
    'QuantumErrorType',
    'ErrorSeverity',
    'DetectionMethod',
    'QuantumError',
    'DetectionResult',
    'QuantumErrorDetector',
    'ErrorDetectionEngine',
    'ErrorDetectionStatistics',
    'create_quantum_error',
    'create_detection_result',
    'classify_error_severity',
    'create_quantum_error_detector',
    'get_error_detection_statistics',
    'create_error_detection_statistics',
    'analyze_detection_batch',
    'get_detection_summary',
    'get_error_summary',
    'test_quantum_error_detector'
]

if __name__ == "__main__":
    test_quantum_error_detector()
