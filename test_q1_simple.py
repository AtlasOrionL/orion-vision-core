#!/usr/bin/env python3
"""
🧪 Simple Q1 Test

Basit Q1 test scripti - debug interface olmadan
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test basic imports"""
    print("🧪 Testing imports...")
    
    try:
        # Test screen capture
        from jobone.vision_core.perception.screen_capture import ScreenCapture
        print("✅ ScreenCapture imported")
        
        # Test OCR processor
        from jobone.vision_core.perception.ocr_processor import OCRProcessor
        print("✅ OCRProcessor imported")
        
        # Test Planck unit
        from jobone.vision_core.quantum.planck_information_unit import create_planck_information_unit
        print("✅ PlanckInformationUnit imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_screen_capture():
    """Test screen capture"""
    print("\n📸 Testing Screen Capture...")
    
    try:
        from jobone.vision_core.perception.screen_capture import ScreenCapture
        
        sc = ScreenCapture()
        print(f"✅ ScreenCapture created (active: {sc.capture_active})")
        
        # Test capture
        img_array = sc.capture_full_screen_as_np_array()
        
        if img_array is not None:
            print(f"✅ Screen captured: {img_array.shape}")
            
            # Get statistics
            stats = sc.get_capture_statistics()
            print(f"📊 Stats: {stats['total_captures']} captures, {stats['captures_per_second']:.1f} FPS")
            
            return True
        else:
            print("❌ Screen capture returned None")
            return False
            
    except Exception as e:
        print(f"❌ Screen capture failed: {e}")
        return False

def test_ocr_processor():
    """Test OCR processor"""
    print("\n📝 Testing OCR Processor...")
    
    try:
        from jobone.vision_core.perception.ocr_processor import OCRProcessor
        import numpy as np
        
        ocr = OCRProcessor()
        print(f"✅ OCRProcessor created (active: {ocr.ocr_active})")
        
        # Create test image
        test_img = np.ones((300, 600, 3), dtype=np.uint8) * 255  # White image
        
        # Test OCR
        result = ocr.detect_text_regions(test_img)
        
        print(f"✅ OCR processed: {result['total_regions']} regions found")
        
        # Show detected text
        for i, region in enumerate(result['text_regions'][:3]):
            print(f"  {i+1}. '{region['text']}' (confidence: {region['confidence']:.2f})")
        
        # Get statistics
        stats = ocr.get_ocr_statistics()
        print(f"📊 Stats: {stats['total_ocr_operations']} operations, {stats['operations_per_second']:.1f} ops/sec")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR processing failed: {e}")
        return False

def test_planck_unit():
    """Test Planck Information Unit"""
    print("\n⚛️ Testing Planck Information Unit...")
    
    try:
        from jobone.vision_core.quantum.planck_information_unit import create_planck_information_unit
        
        planck_unit = create_planck_information_unit()
        print("✅ PlanckInformationUnit created")
        
        # Test basic functionality
        if hasattr(planck_unit, 'get_status'):
            status = planck_unit.get_status()
            print(f"📊 Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Planck unit test failed: {e}")
        return False

def test_lepton_generation():
    """Test Lepton generation from OCR results"""
    print("\n🔬 Testing Lepton Generation...")
    
    try:
        # Simulate OCR results
        ocr_results = [
            {'text': 'Debug Interface', 'confidence': 0.95, 'bbox': (100, 50, 200, 80)},
            {'text': 'Q1 Test Active', 'confidence': 0.88, 'bbox': (150, 100, 250, 130)},
            {'text': 'Orion Vision Core', 'confidence': 0.92, 'bbox': (200, 150, 350, 180)}
        ]
        
        # Generate Leptons
        leptons = []
        for i, region in enumerate(ocr_results):
            lepton = {
                'id': f"lepton_{i}",
                'type': 'text',
                'value': region['text'],
                'position': region['bbox'],
                'effective_mass': 0.1,  # Low initial mass
                'polarization': '+' if region['confidence'] > 0.9 else '0',
                'seed': f"q1_test_{i}",
                'temporal_index': i,
                'confidence': region['confidence']
            }
            leptons.append(lepton)
        
        print(f"✅ Generated {len(leptons)} Leptons:")
        for lepton in leptons:
            print(f"  • {lepton['value']} (mass: {lepton['effective_mass']}, confidence: {lepton['confidence']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Lepton generation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Orion Vision Core - Simple Q1 Test")
    print("="*60)
    
    # Test sequence
    tests = [
        ("Imports", test_imports),
        ("Screen Capture", test_screen_capture),
        ("OCR Processor", test_ocr_processor),
        ("Planck Unit", test_planck_unit),
        ("Lepton Generation", test_lepton_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("🎯 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:20} : {status}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED! Q1 is working!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
