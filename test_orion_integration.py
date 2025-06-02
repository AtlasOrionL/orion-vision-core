#!/usr/bin/env python3
"""
🧪 ORION VISION CORE - INTEGRATION TEST
Entegre sistemin test edilmesi için basit test dosyası
"""

import sys
import os
from pathlib import Path

# Proje root'unu sys.path'e ekle
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Import testleri"""
    print("🧪 Testing imports...")
    
    try:
        from orion_config_manager import get_config
        print("✅ orion_config_manager imported successfully")
        
        config = get_config()
        print(f"✅ Config loaded: {config.server.host}:{config.server.port}")
        
    except Exception as e:
        print(f"❌ Config manager import failed: {e}")
        return False
    
    try:
        from orion_component_coordinator import get_coordinator
        print("✅ orion_component_coordinator imported successfully")
        
        coordinator = get_coordinator()
        print(f"✅ Coordinator loaded with {len(coordinator.components)} components")
        
    except Exception as e:
        print(f"❌ Component coordinator import failed: {e}")
        return False
    
    try:
        import orion_unified_launcher
        print("✅ orion_unified_launcher imported successfully")
        
    except Exception as e:
        print(f"❌ Unified launcher import failed: {e}")
        return False
    
    return True

def test_config():
    """Konfigürasyon testleri"""
    print("\n🔧 Testing configuration...")
    
    try:
        from orion_config_manager import get_config
        config = get_config()
        
        # Port çakışmalarını kontrol et
        conflicts = config.check_port_conflicts()
        if conflicts:
            print(f"⚠️ Port conflicts detected: {conflicts}")
        else:
            print("✅ No port conflicts")
        
        # Konfigürasyonu doğrula
        errors = config.validate_config()
        if errors:
            print(f"⚠️ Configuration errors: {errors}")
        else:
            print("✅ Configuration is valid")
        
        # Konfigürasyon özetini göster
        config.print_config_summary()
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_components():
    """Bileşen testleri"""
    print("\n🎯 Testing components...")
    
    try:
        from orion_component_coordinator import get_coordinator
        coordinator = get_coordinator()
        
        print(f"📋 Registered components: {len(coordinator.components)}")
        for name, component in coordinator.components.items():
            optional = "optional" if component.optional else "required"
            print(f"  - {name}: {component.module_path} ({optional})")
        
        # Bağımlılık sırasını test et
        try:
            start_order = coordinator._resolve_dependencies()
            print(f"✅ Dependency resolution successful: {start_order}")
        except Exception as e:
            print(f"❌ Dependency resolution failed: {e}")
            return False
        
        # Durum özetini göster
        coordinator.print_status_summary()
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def test_runner_service():
    """Runner service testini"""
    print("\n🚀 Testing runner service...")
    
    try:
        # Runner service'i import et
        sys.path.insert(0, str(PROJECT_ROOT / "src" / "jobone" / "vision_core"))
        
        from runner_service import app, OLLAMA_BASE_URL, DEFAULT_MODEL
        print("✅ Runner service imported successfully")
        print(f"✅ Ollama URL: {OLLAMA_BASE_URL}")
        print(f"✅ Default model: {DEFAULT_MODEL}")
        
        # FastAPI app'i kontrol et
        print(f"✅ FastAPI app created: {app.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Runner service test failed: {e}")
        return False

def test_ollama_connection():
    """Ollama bağlantı testi"""
    print("\n🤖 Testing Ollama connection...")
    
    try:
        import httpx
        import asyncio
        
        async def check_ollama():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get("http://localhost:11434/api/tags")
                    if response.status_code == 200:
                        data = response.json()
                        models = [model["name"] for model in data.get("models", [])]
                        print(f"✅ Ollama connected, models: {models}")
                        return True
                    else:
                        print(f"⚠️ Ollama responded with status {response.status_code}")
                        return False
            except Exception as e:
                print(f"⚠️ Ollama connection failed: {e}")
                return False
        
        result = asyncio.run(check_ollama())
        return result
        
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                🧪 ORION INTEGRATION TEST                     ║
    ║                                                              ║
    ║  Tüm Orion bileşenlerinin entegrasyonunu test eder          ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_config),
        ("Component Tests", test_components),
        ("Runner Service Tests", test_runner_service),
        ("Ollama Connection Tests", test_ollama_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_name}")
        print('='*60)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*60}")
    print(f"🧪 TEST SUMMARY")
    print('='*60)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Orion integration is ready!")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
