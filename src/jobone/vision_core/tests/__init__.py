#!/usr/bin/env python3
"""
Orion Vision Core Tests Module
Sprint 8.8 - Final Integration and Production Readiness
Orion Vision Core - Autonomous AI Operating System

This module provides comprehensive testing capabilities for all Orion Vision Core
modules and subsystems, ensuring production readiness and system reliability.

Author: Orion Development Team
Version: 8.8.0
Date: 31 Mayıs 2025
"""

# Import test components
from .test_suite import (
    OrionTestSuite, run_test_suite, TestResult, TestCase
)

# Version information
__version__ = "8.8.0"
__author__ = "Orion Development Team"
__email__ = "dev@orionvisioncore.com"
__status__ = "Development"

# Module metadata
__all__ = [
    # Core classes
    'OrionTestSuite',
    'TestCase',
    
    # Enums
    'TestResult',
    
    # Functions
    'run_test_suite',
    
    # Utilities
    'get_test_info'
]

# Module-level logger
import logging
logger = logging.getLogger(__name__)

def get_test_info() -> dict:
    """
    Get test module information.
    
    Returns:
        Dictionary containing test module information
    """
    return {
        'module': 'orion_vision_core.tests',
        'version': __version__,
        'author': __author__,
        'status': __status__,
        'components': {
            'OrionTestSuite': 'Comprehensive test suite for all Orion modules',
            'TestCase': 'Individual test case data structure',
            'TestResult': 'Test result enumeration'
        },
        'features': [
            'Comprehensive module testing',
            'Integration testing',
            'Performance testing',
            'System functionality testing',
            'Import performance testing',
            'Memory usage testing',
            'Configuration testing',
            'Logging system testing',
            'Module initialization testing',
            'Cross-module integration testing',
            'Automated test reporting',
            'Success rate calculation',
            'Error tracking and reporting',
            'Test duration measurement',
            'Production readiness validation'
        ],
        'test_categories': [
            'Core module tests',
            'Integration tests',
            'Performance tests',
            'System functionality tests'
        ],
        'test_types': [
            'Import tests - Module import validation',
            'Initialization tests - Module initialization validation',
            'Functionality tests - Basic functionality validation',
            'Integration tests - Cross-module integration validation',
            'Performance tests - Speed and memory usage validation',
            'System tests - Overall system functionality validation'
        ],
        'modules_tested': [
            'System Manager',
            'LLM API Manager',
            'Brain AI Manager',
            'Task Framework',
            'Workflow Engine',
            'Voice Manager',
            'NLP Processor',
            'Automation Controller',
            'GUI Framework',
            'Desktop Integration',
            'System Dashboard'
        ],
        'integration_tests': [
            'GUI-Dashboard integration',
            'Voice-NLP integration',
            'Brain-LLM integration'
        ],
        'performance_metrics': [
            'Import speed testing',
            'Memory usage monitoring',
            'Module initialization time',
            'Overall test suite duration'
        ],
        'success_criteria': {
            'production_ready': '90% success rate or higher',
            'mostly_ready': '80% success rate or higher',
            'needs_attention': 'Below 80% success rate'
        }
    }

# Module initialization
logger.info(f"📦 Orion Vision Core Tests Module v{__version__} loaded")

# Export version for external access
VERSION = __version__
