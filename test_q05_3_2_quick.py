#!/usr/bin/env python3
"""
🧪 Q05.3.2 Quick Test Suite

Q05.3.2 bileşenlerinin hızlı testi
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_q05_3_2_quick():
    """Quick test Q05.3.2 Quantum Computation Optimization"""
    print("🧪 Q05.3.2 QUICK TEST")
    print("=" * 40)
    
    try:
        # Test 1: Quantum Algorithm Engine
        print("\n🧮 Test 1: Quantum Algorithm Engine")
        from jobone.vision_core.quantum.quantum_algorithms import test_quantum_algorithms
        test_quantum_algorithms()
        print("✅ Quantum Algorithm Engine - PASSED")
        
        # Test 2: Parallel Quantum Processor
        print("\n⚡ Test 2: Parallel Quantum Processor")
        from jobone.vision_core.quantum.parallel_quantum import test_parallel_quantum
        test_parallel_quantum()
        print("✅ Parallel Quantum Processor - PASSED")
        
        # Test 3: Quantum Speedup Optimizer
        print("\n🚀 Test 3: Quantum Speedup Optimizer")
        from jobone.vision_core.quantum.speedup_optimizer import test_speedup_optimizer
        test_speedup_optimizer()
        print("✅ Quantum Speedup Optimizer - PASSED")
        
        # Test 4: Hybrid Quantum Processor
        print("\n🔄 Test 4: Hybrid Quantum Processor")
        from jobone.vision_core.quantum.hybrid_processor import test_hybrid_processor
        test_hybrid_processor()
        print("✅ Hybrid Quantum Processor - PASSED")
        
        # Test 5: Import Test
        print("\n📦 Test 5: Import Test")
        from jobone.vision_core.quantum import (
            QuantumAlgorithmEngine, ParallelQuantumProcessor,
            QuantumSpeedupOptimizer, HybridQuantumProcessor,
            AlgorithmType, ParallelizationType, OptimizationType, HybridType
        )
        print("✅ All Q05.3.2 components imported successfully")
        
        # Test 6: Status Check
        print("\n📊 Test 6: Status Check")
        from jobone.vision_core.quantum import QFD_STATUS
        print(f"✅ QFD Status: Sprint {QFD_STATUS['sprint']}, Progress {QFD_STATUS['progress']}")
        print(f"✅ Components ready: {len(QFD_STATUS['components_ready'])}")
        print(f"✅ Q05.3.2 components: 4 new components added")
        
        print("\n🎉 Q05.3.2 QUICK TEST BAŞARILI!")
        print("=" * 40)
        print("✅ Quantum algorithm implementation - WORKING")
        print("✅ Parallel quantum processing - WORKING") 
        print("✅ Quantum speedup optimization - WORKING")
        print("✅ Classical-quantum hybrid processing - WORKING")
        print()
        print("📊 Q05.3.2 İlerleme: %100 (4/4 tamamlandı)")
        print("🎯 Sonraki Adım: Q05.4.1 ALT_LAS Kuantum Interface")
        print()
        print("🚀 WAKE UP ORION! Q05.3.2 WORKING! 💖")
        print("🎵 DUYGULANDIK! Kuantum hesaplama optimizasyonu hazır! 🎵")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_q05_3_2_quick()
    if success:
        print("\n🎊 Q05.3.2 quick test başarılı! 🎊")
        exit(0)
    else:
        print("\n💔 Test failed.")
        exit(1)
