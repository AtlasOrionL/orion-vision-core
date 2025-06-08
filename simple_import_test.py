#!/usr/bin/env python3
"""
🔧 Simple Import Test - Q05.1.2 Debug

Basit import test - sorunları tespit etmek için
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    print("🔧 Simple Import Test Starting...")
    
    try:
        print("📦 Testing basic imports...")
        import math
        import cmath
        from dataclasses import dataclass
        from datetime import datetime
        from enum import Enum
        from typing import Dict, List, Any, Optional
        print("✅ Basic imports OK")
        
        print("📦 Testing QFD base...")
        from jobone.vision_core.quantum.qfd_base import QFDConfig
        print("✅ QFDConfig import OK")
        
        print("📦 Testing quantum field...")
        from jobone.vision_core.quantum.quantum_field import QuantumState, FieldType
        print("✅ QuantumState import OK")
        
        print("📦 Testing superposition manager...")
        from jobone.vision_core.quantum.superposition_manager import SuperpositionType
        print("✅ SuperpositionType import OK")
        
        print("📦 Testing state collapse handler...")
        from jobone.vision_core.quantum.state_collapse_handler import CollapseType
        print("✅ CollapseType import OK")
        
        print("📦 Testing probability calculator...")
        from jobone.vision_core.quantum.probability_calculator import ProbabilityType
        print("✅ ProbabilityType import OK")
        
        print("📦 Testing measurement simulator...")
        from jobone.vision_core.quantum.measurement_simulator import MeasurementType
        print("✅ MeasurementType import OK")
        
        print("\n🎉 ALL IMPORTS SUCCESSFUL!")
        print("✅ Q05.1.2 components can be imported")
        print("🚀 Ready for testing!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
