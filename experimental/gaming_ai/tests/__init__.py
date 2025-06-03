"""
🎮 Gaming AI Test Suite

Modular testing framework for Gaming AI components.

Sprint 1 - Task 1.4: Testing Framework
- Modular test structure
- Performance benchmarks
- 90%+ test coverage target

Author: Nexus - Quantum AI Architect
"""

__version__ = "1.0.0"
__author__ = "Nexus - Gaming AI Team"

# Test modules
__all__ = [
    "test_vision",
    "test_ocr", 
    "test_capture",
    "test_performance",
    "test_integration"
]

# Test configuration
TEST_CONFIG = {
    "vision": {
        "test_images_path": "test_data/images/",
        "benchmark_fps": 60,
        "accuracy_threshold": 0.95
    },
    "ocr": {
        "test_texts_path": "test_data/texts/",
        "accuracy_threshold": 0.98,
        "languages": ["en", "tr"]
    },
    "capture": {
        "performance_threshold_ms": 5,
        "memory_threshold_mb": 100,
        "test_duration_sec": 10
    }
}

def get_test_config():
    """Get test configuration"""
    return TEST_CONFIG.copy()
