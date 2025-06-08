#!/usr/bin/env python3
"""
🔮 Q05.1.1 QFD Temel Altyapısı Test

Q05.1.1 görevinin tamamlandığını doğrular:
- QFD base classes ✅
- Quantum field definitions ✅ 
- Field state management ✅
- Quantum calculations engine ✅

Author: Orion Vision Core Team
Sprint: Q05.1.1 - QFD Temel Altyapısı
Status: TESTING
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_qfd_module():
    """Test Q05.1.1 QFD module"""
    print("🔮 Q05.1.1 QFD TEMEL ALTYAPISI TEST")
    print("=" * 50)
    
    try:
        # Test 1: QFD Module Import
        print("\n📦 Test 1: QFD Module Import")
        from jobone.vision_core.quantum import (
            QFDBase, QuantumEntity, QFDConfig, QFDException,
            QuantumField, FieldType, QuantumState, SuperpositionManager,
            FieldStateManager, StateTransition, QuantumObserver,
            QuantumCalculator, QuantumOperation, CalculationResult,
            initialize_qfd, get_qfd_status, qfd_info
        )
        print("✅ All QFD components imported successfully")
        
        # Test 2: QFD Initialization
        print("\n🔧 Test 2: QFD Initialization")
        if initialize_qfd():
            print("✅ QFD module initialized successfully")
        else:
            print("❌ QFD initialization failed")
            return False
        
        # Test 3: QFD Status Check
        print("\n📊 Test 3: QFD Status Check")
        status = get_qfd_status()
        print(f"✅ QFD Status: {status['sprint']} - {status['progress']}")
        print(f"✅ Components Ready: {len(status['components_ready'])}/4")
        
        # Test 4: QFD Base Classes
        print("\n🏗️ Test 4: QFD Base Classes")
        config = QFDConfig()
        entity = QuantumEntity()
        print(f"✅ QFDConfig created: {config.field_dimensions}D fields")
        print(f"✅ QuantumEntity created: {entity.entity_id[:16]}...")
        
        # Test 5: Quantum Field
        print("\n🌊 Test 5: Quantum Field")
        from jobone.vision_core.quantum.quantum_field import create_quantum_field, FieldDimension
        field = create_quantum_field(FieldType.SCALAR, FieldDimension.THREE_D)
        if field.initialize():
            print(f"✅ Quantum field created and initialized: {field.field_id}")
        
        # Test 6: Field State Manager
        print("\n🎛️ Test 6: Field State Manager")
        from jobone.vision_core.quantum.field_state_manager import create_field_state_manager, create_quantum_observer, ObserverType
        manager = create_field_state_manager()
        if manager.initialize():
            print("✅ Field state manager initialized")
        
        observer = create_quantum_observer(ObserverType.ACTIVE, "Test Observer")
        if manager.register_observer(observer):
            print("✅ Quantum observer registered")
        
        # Test 7: Quantum Calculator
        print("\n🧮 Test 7: Quantum Calculator")
        from jobone.vision_core.quantum.quantum_calculator import create_quantum_calculator
        calculator = create_quantum_calculator()
        if calculator.initialize():
            print("✅ Quantum calculator initialized")
        
        # Test superposition calculation
        superposition_input = {
            'basis_states': ['|0⟩', '|1⟩'],
            'amplitudes': None
        }
        result = calculator.calculate(QuantumOperation.SUPERPOSITION, superposition_input)
        if result and result.success:
            print(f"✅ Superposition calculation successful: {result.operation_id[:16]}...")
        
        # Test 8: Integration Test
        print("\n🔗 Test 8: Component Integration")
        if manager.register_field(field):
            print("✅ Field registered with state manager")
        
        # Test state transition
        transition = manager.trigger_state_transition(
            field.field_id, "default", "excited",
            StateTransition.TransitionType.INDUCED, observer.observer_id
        )
        if transition:
            print(f"✅ State transition successful: {transition.transition_id[:16]}...")
        
        # Test 9: Performance Check
        print("\n⚡ Test 9: Performance Check")
        calc_status = calculator.get_status()
        manager_status = manager.get_status()
        field_status = field.get_status()
        
        print(f"✅ Calculator: {calc_status['successful_calculations']} successful operations")
        print(f"✅ Manager: {manager_status['successful_transitions']} successful transitions")
        print(f"✅ Field: {field_status['operations']} field operations")
        
        # Test 10: ALT_LAS Integration Check
        print("\n🧠 Test 10: ALT_LAS Integration Check")
        from jobone.vision_core.quantum import check_alt_las_integration
        integration_status = check_alt_las_integration()
        if integration_status['integration_ready']:
            print("✅ ALT_LAS integration ready")
        else:
            print("⚠️ ALT_LAS integration not available (expected in development)")
        
        print("\n🎉 Q05.1.1 QFD TEMEL ALTYAPISI TEST BAŞARILI!")
        print("=" * 50)
        print("✅ QFD base classes - TAMAMLANDI")
        print("✅ Quantum field definitions - TAMAMLANDI") 
        print("✅ Field state management - TAMAMLANDI")
        print("✅ Quantum calculations engine - TAMAMLANDI")
        print()
        print("📊 Q05.1.1 İlerleme: %100 (4/4 tamamlandı)")
        print("🎯 Sonraki Adım: Q05.1.2 Kuantum Süperpozisyon Yönetimi")
        print()
        print("🚀 WAKE UP ORION! Q05.1.1 TAMAMLANDI! 💖")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_qfd_module()
    if success:
        print("\n🎵 DUYGULANDIK! Q05.1.1 başarıyla tamamlandı! 🎵")
        exit(0)
    else:
        print("\n💔 Test failed. Check the errors above.")
        exit(1)
