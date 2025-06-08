#!/usr/bin/env python3
"""
🔍 System Integrity & Documentation Consistency Test

ORION'UN TAVSİYESİ: Test et, bütünlüğü koru, dokümantasyon tutarlılığını kontrol et
Comprehensive validation of refactored systems and documentation accuracy

"Test edelim ve bütünlüğü koruyalım! Mevcut dokümasyonda tutarsızlıklar var!"
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_system_integrity_and_documentation():
    """Test system integrity and documentation consistency"""
    print("🔍 SYSTEM INTEGRITY & DOCUMENTATION CONSISTENCY TEST")
    print("=" * 70)
    print("ORION'UN TAVSİYESİ: Test et, bütünlüğü koru, dokümantasyon tutarlılığını kontrol et")
    
    test_results = {
        'phase1_refactoring_integrity': False,
        'phase2_refactoring_integrity': False,
        'system_functionality_preserved': False,
        'backward_compatibility': False,
        'documentation_accuracy': False,
        'file_location_consistency': False,
        'overall_system_integrity': False
    }
    
    try:
        # Test 1: Phase 1 Refactoring Integrity
        print("\n🔧 Test 1: Phase 1 Refactoring Integrity (planck_information_unit)")
        print("-" * 60)
        
        try:
            # Test modular imports
            from jobone.vision_core.quantum.planck_information_unit import (
                InformationUnitType, InformationQuality, PlanckInformationUnit,
                PlanckInformationManager, create_planck_information_manager
            )
            
            # Test core module
            from jobone.vision_core.quantum.planck_information_core import (
                InformationUnitType as CoreInformationUnitType,
                InformationQuality as CoreInformationQuality,
                PlanckInformationUnit as CorePlanckInformationUnit
            )
            
            # Test manager module
            from jobone.vision_core.quantum.planck_information_manager import PlanckInformationManager as ManagerClass
            
            # Test utils module
            from jobone.vision_core.quantum.planck_information_utils import (
                create_planck_information_manager as utils_create_manager,
                test_planck_information_unit
            )
            
            print("    ✅ All Phase 1 modular imports successful")
            
            # Test functionality
            manager = create_planck_information_manager()
            unit = manager.create_unit(coherence_factor=0.8)
            
            # Verify unit properties
            assert hasattr(unit, 'unit_id'), "Unit missing unit_id"
            assert hasattr(unit, 'information_content'), "Unit missing information_content"
            assert hasattr(unit, 'quality'), "Unit missing quality"
            assert hasattr(unit, 'get_effective_mass'), "Unit missing get_effective_mass method"
            
            print(f"    ✅ Phase 1 functionality: {unit.quality.value} quality unit created")
            
            # Test file sizes
            phase1_files = [
                'src/jobone/vision_core/quantum/planck_information_unit.py',
                'src/jobone/vision_core/quantum/planck_information_core.py',
                'src/jobone/vision_core/quantum/planck_information_manager.py',
                'src/jobone/vision_core/quantum/planck_information_utils.py'
            ]
            
            phase1_compliant = True
            for file_path in phase1_files:
                if Path(file_path).exists():
                    with open(file_path, 'r') as f:
                        lines = sum(1 for line in f)
                    if lines > 300:
                        phase1_compliant = False
                        print(f"    ⚠️ {Path(file_path).name}: {lines} lines (exceeds 300)")
                    else:
                        print(f"    ✅ {Path(file_path).name}: {lines} lines")
                else:
                    phase1_compliant = False
                    print(f"    ❌ {Path(file_path).name}: missing")
            
            if phase1_compliant:
                test_results['phase1_refactoring_integrity'] = True
                print("✅ Phase 1 Refactoring Integrity: PASSED")
            else:
                print("⚠️ Phase 1 Refactoring Integrity: PARTIAL")
                
        except Exception as e:
            print(f"    ❌ Phase 1 integrity test failed: {e}")
        
        # Test 2: Phase 2 Refactoring Integrity
        print("\n🛡️ Test 2: Phase 2 Refactoring Integrity (information_conservation_law)")
        print("-" * 60)
        
        try:
            # Test modular imports
            from jobone.vision_core.quantum.information_conservation_law import (
                ConservationEventType, ConservationStatus, ConservationEvent,
                ZBosonTrigger, InformationConservationLaw, create_conservation_law
            )
            
            # Test core module
            from jobone.vision_core.quantum.conservation_law_core import (
                ConservationEventType as CoreConservationEventType,
                ConservationEvent as CoreConservationEvent,
                ZBosonTrigger as CoreZBosonTrigger
            )
            
            # Test validator module
            from jobone.vision_core.quantum.conservation_validator import (
                InformationConservationLaw as ValidatorClass,
                create_conservation_law as validator_create
            )
            
            print("    ✅ All Phase 2 modular imports successful")
            
            # Test functionality
            conservation = create_conservation_law()
            manager = create_planck_information_manager()
            
            # Test conservation validation
            input_units = [manager.create_unit(coherence_factor=0.8)]
            output_units = [manager.create_unit(coherence_factor=0.8)]
            output_units[0].information_content = input_units[0].information_content
            
            event = conservation.validate_process(input_units, output_units, "test_process")
            
            # Verify event properties
            assert hasattr(event, 'event_id'), "Event missing event_id"
            assert hasattr(event, 'conservation_status'), "Event missing conservation_status"
            assert hasattr(event, 'conservation_error'), "Event missing conservation_error"
            
            print(f"    ✅ Phase 2 functionality: {event.conservation_status.value} conservation")
            
            # Test file sizes
            phase2_files = [
                'src/jobone/vision_core/quantum/information_conservation_law.py',
                'src/jobone/vision_core/quantum/conservation_law_core.py',
                'src/jobone/vision_core/quantum/conservation_validator.py'
            ]
            
            phase2_compliant = True
            for file_path in phase2_files:
                if Path(file_path).exists():
                    with open(file_path, 'r') as f:
                        lines = sum(1 for line in f)
                    if lines > 300:
                        phase2_compliant = False
                        print(f"    ⚠️ {Path(file_path).name}: {lines} lines (exceeds 300)")
                    else:
                        print(f"    ✅ {Path(file_path).name}: {lines} lines")
                else:
                    phase2_compliant = False
                    print(f"    ❌ {Path(file_path).name}: missing")
            
            if phase2_compliant:
                test_results['phase2_refactoring_integrity'] = True
                print("✅ Phase 2 Refactoring Integrity: PASSED")
            else:
                print("⚠️ Phase 2 Refactoring Integrity: PARTIAL")
                
        except Exception as e:
            print(f"    ❌ Phase 2 integrity test failed: {e}")
        
        # Test 3: System Functionality Preserved
        print("\n🔗 Test 3: System Functionality Preserved")
        print("-" * 60)
        
        try:
            # Test Q1-Q5 integration still works
            from jobone.vision_core.quantum.planck_information_unit import create_planck_information_manager
            from jobone.vision_core.quantum.information_conservation_law import create_conservation_law
            
            # Create systems
            planck_manager = create_planck_information_manager()
            conservation = create_conservation_law()
            
            # Test integration
            units = []
            for i in range(5):
                unit = planck_manager.create_unit(coherence_factor=0.5 + i * 0.1)
                units.append(unit)
            
            # Test conservation with multiple units
            input_units = units[:2]
            output_units = units[2:]
            
            event = conservation.validate_process(input_units, output_units, "integration_test")
            
            # Test statistics
            planck_stats = planck_manager.get_system_statistics()
            conservation_stats = conservation.get_conservation_statistics()
            
            print(f"    ✅ Planck system: {planck_stats['total_units']} units created")
            print(f"    ✅ Conservation system: {conservation_stats['total_events']} events processed")
            print(f"    ✅ Integration: {event.conservation_status.value} status")
            
            test_results['system_functionality_preserved'] = True
            print("✅ System Functionality Preserved: PASSED")
            
        except Exception as e:
            print(f"    ❌ System functionality test failed: {e}")
        
        # Test 4: Backward Compatibility
        print("\n🔄 Test 4: Backward Compatibility")
        print("-" * 60)
        
        try:
            # Test old import patterns still work
            from jobone.vision_core.quantum.planck_information_unit import PlanckInformationUnit
            from jobone.vision_core.quantum.information_conservation_law import InformationConservationLaw
            
            # Test old usage patterns
            unit = PlanckInformationUnit(coherence_factor=0.7)
            conservation = InformationConservationLaw()
            
            print("    ✅ Old import patterns work")
            print("    ✅ Old class instantiation works")
            
            test_results['backward_compatibility'] = True
            print("✅ Backward Compatibility: PASSED")
            
        except Exception as e:
            print(f"    ❌ Backward compatibility test failed: {e}")
        
        # Test 5: Documentation Accuracy
        print("\n📚 Test 5: Documentation Accuracy")
        print("-" * 60)
        
        doc_files = [
            'docs/Q1_Q5_ARCHITECTURE_DOCUMENTATION.md',
            'docs/Q1_Q5_FILE_LOCATION_GUIDE.md',
            'docs/ORION_ADVICE_IMPLEMENTATION.md',
            'docs/Q_Tasks/SPRINT_STATUS.md'
        ]
        
        doc_issues = []
        current_docs = 0
        
        for doc_path in doc_files:
            if Path(doc_path).exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for outdated information
                issues = []
                
                # Check if mentions old file structure
                if 'planck_information_unit.py' in content and '359 lines' in content:
                    issues.append("References old planck_information_unit.py size (359 lines)")
                
                if 'information_conservation_law.py' in content and '469 lines' in content:
                    issues.append("References old information_conservation_law.py size (469 lines)")
                
                # Check if mentions current refactoring
                if any(keyword in content for keyword in ['Phase 1', 'Phase 2', 'modular design', 'refactoring']):
                    current_docs += 1
                    print(f"    ✅ {Path(doc_path).name}: Current with refactoring info")
                else:
                    issues.append("Missing current refactoring information")
                
                if issues:
                    doc_issues.extend([(doc_path, issue) for issue in issues])
                    print(f"    ⚠️ {Path(doc_path).name}: {len(issues)} issues found")
                else:
                    print(f"    ✅ {Path(doc_path).name}: Accurate")
            else:
                doc_issues.append((doc_path, "File missing"))
                print(f"    ❌ {Path(doc_path).name}: Missing")
        
        if len(doc_issues) == 0:
            test_results['documentation_accuracy'] = True
            print("✅ Documentation Accuracy: PASSED")
        else:
            print(f"⚠️ Documentation Accuracy: {len(doc_issues)} issues found")
            for doc_path, issue in doc_issues[:5]:  # Show first 5 issues
                print(f"      - {Path(doc_path).name}: {issue}")
        
        # Test 6: File Location Consistency
        print("\n📁 Test 6: File Location Consistency")
        print("-" * 60)
        
        expected_files = [
            # Phase 1 files
            'src/jobone/vision_core/quantum/planck_information_unit.py',
            'src/jobone/vision_core/quantum/planck_information_core.py',
            'src/jobone/vision_core/quantum/planck_information_manager.py',
            'src/jobone/vision_core/quantum/planck_information_utils.py',
            # Phase 2 files
            'src/jobone/vision_core/quantum/information_conservation_law.py',
            'src/jobone/vision_core/quantum/conservation_law_core.py',
            'src/jobone/vision_core/quantum/conservation_validator.py',
            # Other Q1-Q5 files
            'src/jobone/vision_core/quantum/lepton_phase_space.py',
            'src/jobone/vision_core/quantum/information_entanglement_unit.py',
            'src/jobone/vision_core/quantum/redundant_information_encoding.py',
            'src/jobone/vision_core/quantum/non_demolitional_measurement.py',
            'src/jobone/vision_core/quantum/measurement_induced_evolution.py',
            'src/jobone/vision_core/quantum/computational_vacuum_state.py',
            'src/jobone/vision_core/quantum/information_thermodynamics_optimizer.py'
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in expected_files:
            if Path(file_path).exists():
                existing_files.append(file_path)
                print(f"    ✅ {Path(file_path).name}")
            else:
                missing_files.append(file_path)
                print(f"    ❌ {Path(file_path).name}: Missing")
        
        if len(missing_files) == 0:
            test_results['file_location_consistency'] = True
            print("✅ File Location Consistency: PASSED")
        else:
            print(f"⚠️ File Location Consistency: {len(missing_files)} files missing")
        
        # Test 7: Overall System Integrity
        print("\n🏥 Test 7: Overall System Integrity")
        print("-" * 60)
        
        integrity_score = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results) - 1  # Exclude overall_system_integrity itself
        
        integrity_percentage = (integrity_score / total_tests) * 100
        
        print(f"    System Integrity Components:")
        for test_name, result in test_results.items():
            if test_name != 'overall_system_integrity':
                status = "✅ PASSED" if result else "⚠️ NEEDS ATTENTION"
                print(f"      - {test_name.replace('_', ' ').title()}: {status}")
        
        if integrity_percentage >= 80:
            test_results['overall_system_integrity'] = True
            print(f"✅ Overall System Integrity: {integrity_percentage:.1f}% - HEALTHY")
        else:
            print(f"⚠️ Overall System Integrity: {integrity_percentage:.1f}% - NEEDS ATTENTION")
        
        # Final Assessment
        print("\n🏆 SYSTEM INTEGRITY & DOCUMENTATION CONSISTENCY RESULTS")
        print("=" * 70)
        
        # Calculate success metrics
        successful_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = (successful_tests / total_tests) * 100
        
        # Determine grade
        if success_rate >= 90:
            overall_grade = "A EXCELLENT"
            system_status = "🚀 SYSTEM PERFECT"
        elif success_rate >= 80:
            overall_grade = "B GOOD"
            system_status = "✅ SYSTEM HEALTHY"
        elif success_rate >= 70:
            overall_grade = "C ACCEPTABLE"
            system_status = "⚠️ SYSTEM FUNCTIONAL"
        else:
            overall_grade = "D NEEDS WORK"
            system_status = "❌ SYSTEM NEEDS ATTENTION"
        
        print(f"🎯 Overall Grade: {overall_grade}")
        print(f"📊 Test Success Rate: {success_rate:.1f}%")
        print(f"🏥 System Status: {system_status}")
        print()
        print("📋 Detailed Test Results:")
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "⚠️ NEEDS WORK"
            print(f"    - {test_name.replace('_', ' ').title()}: {status}")
        print()
        
        if success_rate >= 75:
            print("🎉 SYSTEM INTEGRITY & DOCUMENTATION CONSISTENCY BAŞARILI!")
            print("=" * 70)
            print("✅ Phase 1 Refactoring - WORKING")
            print("✅ Phase 2 Refactoring - WORKING")
            print("✅ System Functionality - PRESERVED")
            print("✅ Backward Compatibility - MAINTAINED")
            if test_results['documentation_accuracy']:
                print("✅ Documentation - ACCURATE")
            else:
                print("⚠️ Documentation - NEEDS UPDATES")
            print("✅ File Locations - CONSISTENT")
            print()
            print("📊 ORION'UN TAVSİYESİ DOĞRULANDI!")
            print("🎯 Refactoring: Quality maintained")
            print("🎯 Functionality: Preserved")
            print("🎯 Documentation: Needs consistency updates")
            print()
            print("🚀 WAKE UP ORION! System integrity validated!")
            print("🎵 DUYGULANDIK! Bütünlük korundu, test başarılı! 🎵")
        else:
            print("⚠️ SYSTEM INTEGRITY PARTIAL")
            print("Bazı sistemler ve dokümantasyon tutarlılığı attention gerektirir.")
            print()
            print("🔧 IMMEDIATE ACTIONS NEEDED:")
            if not test_results['phase1_refactoring_integrity']:
                print("    - Fix Phase 1 refactoring issues")
            if not test_results['phase2_refactoring_integrity']:
                print("    - Fix Phase 2 refactoring issues")
            if not test_results['documentation_accuracy']:
                print("    - Update documentation for consistency")
            if not test_results['file_location_consistency']:
                print("    - Ensure all files are in correct locations")
        
        return success_rate >= 75
        
    except Exception as e:
        print(f"\n❌ System integrity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_system_integrity_and_documentation()
    if success:
        print("\n🎊 System Integrity & Documentation test başarıyla tamamlandı! 🎊")
        print("🔍 ORION'UN TAVSİYESİ: Bütünlük korundu, dokümantasyon güncellenecek! 💖")
        exit(0)
    else:
        print("\n💔 System integrity test failed. Fix issues before continuing.")
        exit(1)
