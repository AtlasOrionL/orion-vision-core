#!/usr/bin/env python3
"""
🧹 Temizlik Step 2: Folder Organization
💖 DUYGULANDIK! KÜÇÜK ADIMLAR DEVAM!

STEP 2 GOALS:
- Move files to clean structure
- Organize legacy files
- Create proper structure

Author: Orion Vision Core Team
Status: 🧹 STEP 2 ACTIVE
"""

import os
import shutil

def move_import_files():
    """📦 Import dosyalarını taşı"""
    import_files = [
        'orion_common.py',
        'orion_sprints.py',
        'orion_import_helper.py'
    ]
    
    moved = 0
    for file_name in import_files:
        if os.path.exists(file_name):
            dest = os.path.join('orion_clean', 'imports', file_name)
            try:
                shutil.copy2(file_name, dest)
                moved += 1
            except Exception as e:
                print(f"⚠️ Move warning {file_name}: {e}")
    
    print(f"✅ Step 2.1: {moved} import files moved")

def organize_q04_files():
    """🎯 Q04 dosyalarını organize et"""
    q04_files = [
        'q04_foundation_setup.py',
        'q04_hybrid_start.py',
        'q04_base_classes.py'
    ]
    
    # Q04 klasörü oluştur
    q04_dir = os.path.join('orion_clean', 'core', 'q04')
    os.makedirs(q04_dir, exist_ok=True)
    
    moved = 0
    for file_name in q04_files:
        if os.path.exists(file_name):
            dest = os.path.join(q04_dir, file_name)
            try:
                shutil.copy2(file_name, dest)
                moved += 1
            except Exception as e:
                print(f"⚠️ Q04 move warning {file_name}: {e}")
    
    print(f"✅ Step 2.2: {moved} Q04 files organized")

def organize_test_files():
    """🧪 Test dosyalarını organize et"""
    test_files = [
        'orion_fisilti_test.py',
        'q03_integration_test.py',
        'q03_dans_test.py'
    ]
    
    # Test klasörü oluştur
    test_dir = os.path.join('orion_clean', 'tests')
    os.makedirs(test_dir, exist_ok=True)
    
    moved = 0
    for file_name in test_files:
        if os.path.exists(file_name):
            dest = os.path.join(test_dir, file_name)
            try:
                shutil.copy2(file_name, dest)
                moved += 1
            except Exception as e:
                print(f"⚠️ Test move warning {file_name}: {e}")
    
    print(f"✅ Step 2.3: {moved} test files organized")

def create_structure_map():
    """📋 Yapı haritası oluştur"""
    structure_map = '''# 📁 ORION CLEAN STRUCTURE MAP

## 🧹 Temiz Klasör Yapısı:

```
orion_clean/
├── imports/           # Import modules
│   ├── orion_common.py
│   ├── orion_sprints.py
│   └── orion_import_helper.py
├── core/              # Core modules
│   └── q04/           # Q04 modules
├── tests/             # Test modules
└── utils/             # Utility modules

orion_legacy/          # Legacy files
```

## 🎯 Faydalar:
- ✅ Temiz organizasyon
- ✅ Kolay navigasyon
- ✅ Modüler yapı
- ✅ Bakım kolaylığı

## 🚀 Sonraki Adımlar:
- Step 3: Code standardization
- Step 4: Performance optimization
- Step 5: Final cleanup
'''
    
    with open('STRUCTURE_MAP.md', 'w') as f:
        f.write(structure_map)
    
    print("✅ Step 2.4: Structure map created")

def main():
    """Ana temizlik step 2"""
    print("🧹 TEMIZLIK STEP 2 BAŞLIYOR!")
    print("📁 Folder organization ile devam!")
    
    try:
        move_import_files()
        organize_q04_files()
        organize_test_files()
        create_structure_map()
        
        print("\n✅ STEP 2 TAMAMLANDI!")
        print("📁 Files organized in orion_clean/")
        print("📋 Structure map: STRUCTURE_MAP.md")
        print("\n🚀 Step 3'e hazır!")
        
    except Exception as e:
        print(f"❌ Step 2 error: {e}")

if __name__ == "__main__":
    main()
