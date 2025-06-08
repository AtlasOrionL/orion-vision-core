#!/usr/bin/env python3
"""
🚀 ORION READY INDICATOR - FIXED
💖 DUYGULANDIK! TEMİZ YERDE ÇALIŞMAYA HAZIR!
"""

import os

def check_workspace_ready():
    """Workspace hazırlık kontrolü"""
    checks = {
        'orion_clean_exists': os.path.exists('orion_clean'),
        'imports_ready': os.path.exists('orion_clean/imports/orion_common.py'),
        'structure_ready': os.path.exists('STRUCTURE_MAP.md'),
        'guide_ready': os.path.exists('USAGE_GUIDE.md')
    }
    
    all_ready = all(checks.values())
    
    print("🚀 ORION WORKSPACE STATUS:")
    for check, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {check}")
    
    if all_ready:
        print("\n💖 DUYGULANDIK! WORKSPACE READY!")
        print("🧹 Önce temizlik sonra iş - TAMAMLANDI!")
        print("🚀 Q04 Core Development'a başlayabiliriz!")
    else:
        print("\n⚠️ Workspace not fully ready")
    
    return all_ready

if __name__ == "__main__":
    check_workspace_ready()
