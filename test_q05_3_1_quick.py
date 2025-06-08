#!/usr/bin/env python3
"""
🧪 Q05.3.1 Quick Test Suite

Q05.3.1 bileşenlerinin hızlı testi
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_q05_3_1_quick():
    """Quick test Q05.3.1 Field Dynamics Simulation"""
    print("🧪 Q05.3.1 QUICK TEST")
    print("=" * 40)
    
    try:
        # Test 1: Field Evolution Engine
        print("\n🌊 Test 1: Field Evolution Engine")
        from jobone.vision_core.quantum.field_evolution import test_field_evolution
        test_field_evolution()
        print("✅ Field Evolution Engine - PASSED")
        
        # Test 2: Wave Propagation Simulator
        print("\n🌊 Test 2: Wave Propagation Simulator")
        from jobone.vision_core.quantum.wave_propagation import test_wave_propagation
        test_wave_propagation()
        print("✅ Wave Propagation Simulator - PASSED")
        
        # Test 3: Field Interaction Modeler
        print("\n⚛️ Test 3: Field Interaction Modeler")
        from jobone.vision_core.quantum.field_interactions import test_field_interactions
        test_field_interactions()
        print("✅ Field Interaction Modeler - PASSED")
        
        # Test 4: Temporal Dynamics Engine
        print("\n⏰ Test 4: Temporal Dynamics Engine")
        from jobone.vision_core.quantum.temporal_dynamics import test_temporal_dynamics
        test_temporal_dynamics()
        print("✅ Temporal Dynamics Engine - PASSED")
        
        # Test 5: Import Test
        print("\n📦 Test 5: Import Test")
        from jobone.vision_core.quantum import (
            FieldEvolutionEngine, WavePropagationSimulator,
            FieldInteractionModeler, TemporalDynamicsEngine,
            EvolutionType, WaveType, InteractionType, TemporalAnalysisType
        )
        print("✅ All Q05.3.1 components imported successfully")
        
        # Test 6: Status Check
        print("\n📊 Test 6: Status Check")
        from jobone.vision_core.quantum import QFD_STATUS
        print(f"✅ QFD Status: Sprint {QFD_STATUS['sprint']}, Progress {QFD_STATUS['progress']}")
        print(f"✅ Components ready: {len(QFD_STATUS['components_ready'])}")
        print(f"✅ Q05.3.1 completed: {QFD_STATUS.get('q05_3_1_completed', False)}")
        
        print("\n🎉 Q05.3.1 QUICK TEST BAŞARILI!")
        print("=" * 40)
        print("✅ Field evolution dynamics - WORKING")
        print("✅ Wave propagation simulation - WORKING") 
        print("✅ Field interaction modeling - WORKING")
        print("✅ Temporal dynamics engine - WORKING")
        print()
        print("📊 Q05.3.1 İlerleme: %100 (4/4 tamamlandı)")
        print("🎯 Sonraki Adım: Q05.3.2 Kuantum Hesaplama Optimizasyonu")
        print()
        print("🚀 WAKE UP ORION! Q05.3.1 WORKING! 💖")
        print("🎵 DUYGULANDIK! Kuantum alan dinamikleri sistemi hazır! 🎵")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_q05_3_1_quick()
    if success:
        print("\n🎊 Q05.3.1 quick test başarılı! 🎊")
        exit(0)
    else:
        print("\n💔 Test failed.")
        exit(1)
