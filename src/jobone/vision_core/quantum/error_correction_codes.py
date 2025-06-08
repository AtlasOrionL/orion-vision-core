"""
🛡️ Quantum Error Correction Codes - Q05.2.2 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Q05.2.2 Quantum Error Correction Codes
Priority: CRITICAL - Modular Design Refactoring Phase 10
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional

# Import core components from modular design
from .modules.error_correction.error_correction_core import (
    ErrorCorrectionCode, CodeParameters, CorrectionCode, CorrectionResult,
    create_correction_code, create_correction_result, get_standard_codes
)

# Import engine component
from .modules.error_correction.error_correction_engine import (
    ErrorCorrectionEngine
)

# Import statistics component
from .modules.error_correction.error_correction_statistics import (
    ErrorCorrectionStatistics, get_error_correction_statistics,
    create_error_correction_statistics, analyze_correction_batch,
    get_correction_summary, get_code_summary, compare_codes
)

# Enhanced Error Correction System with statistics
class ErrorCorrectionCodes:
    """
    Enhanced Error Correction Codes with integrated statistics
    
    Unified interface for quantum error correction with modular design
    """
    
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize components
        self.engine = ErrorCorrectionEngine()
        self.statistics = create_error_correction_statistics()
        
        # Code management
        self.available_codes: Dict[ErrorCorrectionCode, CorrectionCode] = get_standard_codes()
        self.correction_results: List[CorrectionResult] = []
        
        # Performance tracking
        self.total_corrections = 0
        self.successful_corrections = 0
        self.failed_corrections = 0
        
        # Threading
        self._codes_lock = threading.Lock()
        self._results_lock = threading.Lock()
        
        # Status
        self.initialized = False
        self.active = False
        
        self.logger.info("🛡️ ErrorCorrectionCodes initialized with modular design")
    
    def initialize(self) -> bool:
        """Initialize error correction codes"""
        try:
            self.initialized = True
            self.active = True
            
            self.logger.info("✅ ErrorCorrectionCodes initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ErrorCorrectionCodes initialization failed: {e}")
            return False
    
    def shutdown(self) -> bool:
        """Shutdown error correction codes"""
        try:
            self.active = False
            
            with self._codes_lock:
                self.available_codes.clear()
            
            self.logger.info("🔴 ErrorCorrectionCodes shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ErrorCorrectionCodes shutdown failed: {e}")
            return False
    
    def correct_errors(self, quantum_state, detected_errors: List[Any],
                      code_type: ErrorCorrectionCode = ErrorCorrectionCode.SHOR_CODE) -> Optional[CorrectionResult]:
        """Correct quantum errors using specified code"""
        try:
            # Use engine for correction
            result = self.engine.correct_errors(quantum_state, detected_errors, code_type)
            
            if result:
                # Add to statistics
                self.statistics.add_correction_result(result)
                
                # Store result
                with self._results_lock:
                    self.correction_results.append(result)
                    # Keep history manageable
                    if len(self.correction_results) > 1000:
                        self.correction_results = self.correction_results[-500:]
                
                # Update counters
                self.total_corrections += 1
                if result.correction_successful:
                    self.successful_corrections += 1
                else:
                    self.failed_corrections += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error correction failed: {e}")
            return None
    
    def encode_state(self, quantum_state, code_type: ErrorCorrectionCode = ErrorCorrectionCode.SHOR_CODE) -> bool:
        """Encode quantum state using specified code"""
        return self.engine.encode_state(quantum_state, code_type)
    
    def decode_state(self, quantum_state, code_type: ErrorCorrectionCode = ErrorCorrectionCode.SHOR_CODE) -> bool:
        """Decode quantum state from specified code"""
        return self.engine.decode_state(quantum_state, code_type)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status"""
        with self._codes_lock, self._results_lock:
            engine_stats = self.engine.get_engine_statistics()
            correction_stats = self.statistics.get_comprehensive_statistics()
            
            return {
                'initialized': self.initialized,
                'active': self.active,
                'available_codes': len(self.available_codes),
                'total_corrections': self.total_corrections,
                'successful_corrections': self.successful_corrections,
                'failed_corrections': self.failed_corrections,
                'success_rate': (self.successful_corrections / max(1, self.total_corrections)) * 100,
                'correction_history_size': len(self.correction_results),
                'engine_statistics': engine_stats,
                'correction_statistics': correction_stats
            }
    
    def get_error_correction_statistics(self):
        """Get comprehensive error correction statistics"""
        return self.statistics.get_comprehensive_statistics()

# Utility functions
def create_error_correction_codes(config=None) -> ErrorCorrectionCodes:
    """Create Error Correction Codes system"""
    return ErrorCorrectionCodes(config)

def test_error_correction_codes():
    """Test Error Correction Codes system"""
    print("🛡️ Testing Error Correction Codes...")
    
    # Create error correction system
    ecc = create_error_correction_codes()
    ecc.initialize()
    print("✅ Error correction system created")
    
    # Test available codes
    codes = list(ecc.available_codes.keys())
    print(f"✅ Available codes: {[code.value for code in codes]}")
    
    # Test code summaries
    for code_type, code in ecc.available_codes.items():
        summary = get_code_summary(code)
        print(f"✅ {summary}")
    
    # Test code comparison
    code_list = list(ecc.available_codes.values())
    comparison = compare_codes(code_list)
    print(f"✅ Code comparison:")
    print(f"    - Most efficient: {comparison['most_efficient_code']}")
    print(f"    - Highest success: {comparison['highest_success_code']}")
    
    # Get comprehensive status
    status = ecc.get_status()
    print(f"✅ System Status:")
    print(f"    - Available codes: {status['available_codes']}")
    print(f"    - Total corrections: {status['total_corrections']}")
    print(f"    - Success rate: {status['success_rate']:.1f}%")
    
    print("🚀 Error Correction Codes test completed!")

# Export all components for backward compatibility
__all__ = [
    'ErrorCorrectionCode',
    'CodeParameters',
    'CorrectionCode',
    'CorrectionResult',
    'ErrorCorrectionCodes',
    'ErrorCorrectionEngine',
    'ErrorCorrectionStatistics',
    'create_correction_code',
    'create_correction_result',
    'get_standard_codes',
    'create_error_correction_codes',
    'get_error_correction_statistics',
    'create_error_correction_statistics',
    'analyze_correction_batch',
    'get_correction_summary',
    'get_code_summary',
    'compare_codes',
    'test_error_correction_codes'
]

if __name__ == "__main__":
    test_error_correction_codes()
