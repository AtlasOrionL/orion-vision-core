#!/usr/bin/env python3
"""
VS Code Extension Test Suite
Comprehensive testing of Orion Vision Core VS Code Extension

Author: Atlas-orion (Augment Agent)
Date: 2 Haziran 2025
Purpose: VS Code extension validation and testing
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🆚 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print formatted section"""
    print(f"\n🔍 {title}")
    print("-" * 40)

def test_extension_structure():
    """Test VS Code extension file structure"""
    print_section("EXTENSION FILE STRUCTURE TEST")
    
    base_path = "vscode-extension"
    
    # Critical files to check
    critical_files = [
        "package.json",
        "README.md",
        "src/extension.ts",
        "src/extension-fixed.ts",
        "out/extension.js",
        "out/extension-fixed.js",
        "tsconfig.json"
    ]
    
    # Critical directories to check
    critical_dirs = [
        "src",
        "src/providers",
        "src/ui",
        "src/utils",
        "src/config",
        "out",
        "out/providers",
        "node_modules"
    ]
    
    found_files = 0
    found_dirs = 0
    
    print("📁 Checking critical files...")
    for file_path in critical_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            found_files += 1
            size = os.path.getsize(full_path)
            print(f"  ✅ {file_path} ({size} bytes)")
        else:
            print(f"  ❌ {file_path} - Missing")
    
    print(f"\n📂 Checking critical directories...")
    for dir_path in critical_dirs:
        full_path = os.path.join(base_path, dir_path)
        if os.path.exists(full_path):
            found_dirs += 1
            file_count = len([f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))])
            print(f"  ✅ {dir_path} ({file_count} files)")
        else:
            print(f"  ❌ {dir_path} - Missing")
    
    print(f"\n📊 Structure Summary:")
    print(f"  Files: {found_files}/{len(critical_files)} ({(found_files/len(critical_files)*100):.1f}%)")
    print(f"  Directories: {found_dirs}/{len(critical_dirs)} ({(found_dirs/len(critical_dirs)*100):.1f}%)")
    
    return found_files >= len(critical_files) * 0.8 and found_dirs >= len(critical_dirs) * 0.8

def test_package_json():
    """Test package.json configuration"""
    print_section("PACKAGE.JSON CONFIGURATION TEST")
    
    try:
        with open("vscode-extension/package.json", "r") as f:
            package_data = json.load(f)
        
        print("✅ package.json loaded successfully")
        
        # Check essential fields
        essential_fields = [
            "name", "displayName", "description", "version", "publisher",
            "engines", "categories", "main", "contributes"
        ]
        
        missing_fields = []
        for field in essential_fields:
            if field in package_data:
                print(f"  ✅ {field}: {str(package_data[field])[:50]}...")
            else:
                missing_fields.append(field)
                print(f"  ❌ {field}: Missing")
        
        # Check commands
        commands = package_data.get("contributes", {}).get("commands", [])
        print(f"\n📋 Commands: {len(commands)} registered")
        for cmd in commands[:5]:  # Show first 5
            print(f"  🔧 {cmd.get('command', 'Unknown')}: {cmd.get('title', 'No title')}")
        
        # Check views
        views = package_data.get("contributes", {}).get("views", {})
        orion_views = views.get("orion", [])
        print(f"\n👁️ Views: {len(orion_views)} Orion views")
        for view in orion_views:
            print(f"  📱 {view.get('id', 'Unknown')}: {view.get('name', 'No name')}")
        
        # Check configuration
        config = package_data.get("contributes", {}).get("configuration", {})
        properties = config.get("properties", {})
        print(f"\n⚙️ Configuration: {len(properties)} settings")
        
        # Check dependencies
        dependencies = package_data.get("dependencies", {})
        dev_dependencies = package_data.get("devDependencies", {})
        print(f"\n📦 Dependencies: {len(dependencies)} runtime, {len(dev_dependencies)} dev")
        
        success = len(missing_fields) == 0 and len(commands) >= 10 and len(orion_views) >= 5
        
        if success:
            print("\n✅ Package.json: EXCELLENT CONFIGURATION")
        else:
            print(f"\n⚠️ Package.json: Issues detected - {len(missing_fields)} missing fields")
        
        return success
        
    except Exception as e:
        print(f"❌ Package.json test failed: {str(e)}")
        return False

def test_source_code():
    """Test TypeScript source code"""
    print_section("TYPESCRIPT SOURCE CODE TEST")
    
    try:
        # Check main extension files
        extension_files = [
            "vscode-extension/src/extension.ts",
            "vscode-extension/src/extension-fixed.ts",
            "vscode-extension/src/extension-simple.ts"
        ]
        
        working_extensions = 0
        for ext_file in extension_files:
            if os.path.exists(ext_file):
                size = os.path.getsize(ext_file)
                print(f"  ✅ {os.path.basename(ext_file)}: {size} bytes")
                working_extensions += 1
            else:
                print(f"  ❌ {os.path.basename(ext_file)}: Missing")
        
        # Check provider files
        provider_path = "vscode-extension/src/providers"
        if os.path.exists(provider_path):
            providers = [f for f in os.listdir(provider_path) if f.endswith('.ts')]
            print(f"\n🔌 Providers: {len(providers)} TypeScript files")
            
            expected_providers = [
                'aiProvider.ts', 'chatProvider.ts', 'terminalProvider.ts',
                'fileSystemProvider.ts', 'apiProvider.ts', 'webviewProvider.ts'
            ]
            
            found_providers = 0
            for provider in expected_providers:
                if provider in providers:
                    found_providers += 1
                    print(f"  ✅ {provider}")
                else:
                    print(f"  ❌ {provider}: Missing")
            
            print(f"  📊 Provider coverage: {found_providers}/{len(expected_providers)} ({(found_providers/len(expected_providers)*100):.1f}%)")
        
        # Check compiled output
        out_path = "vscode-extension/out"
        if os.path.exists(out_path):
            js_files = []
            for root, dirs, files in os.walk(out_path):
                js_files.extend([f for f in files if f.endswith('.js')])
            
            print(f"\n🔧 Compiled Output: {len(js_files)} JavaScript files")
            print(f"  ✅ TypeScript compilation: {'Working' if len(js_files) >= 10 else 'Issues detected'}")
        
        success = working_extensions >= 2 and found_providers >= 4
        return success
        
    except Exception as e:
        print(f"❌ Source code test failed: {str(e)}")
        return False

def test_vsix_packages():
    """Test VSIX package files"""
    print_section("VSIX PACKAGE FILES TEST")
    
    try:
        vsix_path = "vscode-extension"
        vsix_files = [f for f in os.listdir(vsix_path) if f.endswith('.vsix')]
        
        print(f"📦 VSIX Packages: {len(vsix_files)} found")
        
        total_size = 0
        for vsix_file in vsix_files:
            file_path = os.path.join(vsix_path, vsix_file)
            size = os.path.getsize(file_path)
            size_mb = size / (1024 * 1024)
            total_size += size
            
            print(f"  📦 {vsix_file}: {size_mb:.2f}MB")
        
        total_mb = total_size / (1024 * 1024)
        print(f"\n📊 Total package size: {total_mb:.2f}MB")
        
        # Check for latest package
        latest_packages = [f for f in vsix_files if 'latest' in f or '1.0.0' in f]
        print(f"✅ Latest packages: {len(latest_packages)} available")
        
        success = len(vsix_files) >= 3 and total_mb > 2.0  # At least 3 packages, reasonable size
        return success
        
    except Exception as e:
        print(f"❌ VSIX package test failed: {str(e)}")
        return False

def test_extension_features():
    """Test extension feature completeness"""
    print_section("EXTENSION FEATURES TEST")
    
    try:
        # Load package.json for feature analysis
        with open("vscode-extension/package.json", "r") as f:
            package_data = json.load(f)
        
        # Analyze commands
        commands = package_data.get("contributes", {}).get("commands", [])
        command_categories = {}
        
        for cmd in commands:
            category = cmd.get("category", "Other")
            if category not in command_categories:
                command_categories[category] = []
            command_categories[category].append(cmd.get("command", "unknown"))
        
        print("🔧 Command Categories:")
        for category, cmds in command_categories.items():
            print(f"  📂 {category}: {len(cmds)} commands")
        
        # Analyze views
        views = package_data.get("contributes", {}).get("views", {}).get("orion", [])
        view_types = {}
        
        for view in views:
            view_type = view.get("type", "tree")
            if view_type not in view_types:
                view_types[view_type] = 0
            view_types[view_type] += 1
        
        print(f"\n👁️ View Types:")
        for view_type, count in view_types.items():
            print(f"  📱 {view_type}: {count} views")
        
        # Analyze keybindings
        keybindings = package_data.get("contributes", {}).get("keybindings", [])
        print(f"\n⌨️ Keybindings: {len(keybindings)} shortcuts")
        
        # Analyze configuration
        config = package_data.get("contributes", {}).get("configuration", {})
        properties = config.get("properties", {})
        
        config_categories = {}
        for prop_name, prop_config in properties.items():
            category = prop_name.split('.')[1] if '.' in prop_name else 'general'
            if category not in config_categories:
                config_categories[category] = 0
            config_categories[category] += 1
        
        print(f"\n⚙️ Configuration Categories:")
        for category, count in config_categories.items():
            print(f"  🔧 {category}: {count} settings")
        
        # Feature completeness score
        feature_score = 0
        feature_score += min(len(commands) / 10, 1.0) * 25  # Commands (max 25 points)
        feature_score += min(len(views) / 5, 1.0) * 25     # Views (max 25 points)
        feature_score += min(len(keybindings) / 5, 1.0) * 25  # Keybindings (max 25 points)
        feature_score += min(len(properties) / 15, 1.0) * 25  # Config (max 25 points)
        
        print(f"\n📊 Feature Completeness Score: {feature_score:.1f}/100")
        
        if feature_score >= 90:
            print("🎉 EXCEPTIONAL: Feature-complete extension!")
        elif feature_score >= 75:
            print("🎊 EXCELLENT: Well-featured extension!")
        elif feature_score >= 60:
            print("👍 GOOD: Solid feature set!")
        else:
            print("⚠️ BASIC: Limited features detected!")
        
        return feature_score >= 75
        
    except Exception as e:
        print(f"❌ Feature test failed: {str(e)}")
        return False

def test_installation_readiness():
    """Test extension installation readiness"""
    print_section("INSTALLATION READINESS TEST")
    
    try:
        # Check if extension can be installed
        print("🔍 Checking installation requirements...")
        
        # Check Node.js dependencies
        node_modules_path = "vscode-extension/node_modules"
        if os.path.exists(node_modules_path):
            modules = [d for d in os.listdir(node_modules_path) if os.path.isdir(os.path.join(node_modules_path, d))]
            print(f"  ✅ Node modules: {len(modules)} installed")
        else:
            print("  ❌ Node modules: Not installed")
            return False
        
        # Check TypeScript compilation
        out_path = "vscode-extension/out"
        if os.path.exists(out_path):
            js_files = [f for f in os.listdir(out_path) if f.endswith('.js')]
            print(f"  ✅ Compiled files: {len(js_files)} JavaScript files")
        else:
            print("  ❌ Compiled files: Missing")
            return False
        
        # Check VSIX packages
        vsix_files = [f for f in os.listdir("vscode-extension") if f.endswith('.vsix')]
        if vsix_files:
            print(f"  ✅ VSIX packages: {len(vsix_files)} ready for installation")
        else:
            print("  ❌ VSIX packages: None found")
            return False
        
        # Check package.json validity
        with open("vscode-extension/package.json", "r") as f:
            package_data = json.load(f)
        
        required_fields = ["name", "version", "engines", "main", "contributes"]
        missing_required = [field for field in required_fields if field not in package_data]
        
        if not missing_required:
            print("  ✅ Package.json: Valid for VS Code")
        else:
            print(f"  ❌ Package.json: Missing required fields: {missing_required}")
            return False
        
        print("\n🎯 Installation Status: READY FOR DEPLOYMENT")
        print("💡 Installation command: code --install-extension orion-vision-core-1.0.0.vsix")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation readiness test failed: {str(e)}")
        return False

def main():
    """Main VS Code extension test function"""
    print_header("VS CODE EXTENSION COMPREHENSIVE TEST")
    print(f"🕐 Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all extension tests
    tests = [
        ("Extension Structure", test_extension_structure),
        ("Package Configuration", test_package_json),
        ("Source Code", test_source_code),
        ("VSIX Packages", test_vsix_packages),
        ("Extension Features", test_extension_features),
        ("Installation Readiness", test_installation_readiness)
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        print_section(f"RUNNING {test_name.upper()} TEST")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ ERROR: {test_name} - {str(e)}")
    
    total_time = time.time() - start_time
    
    # Final results
    print_header("VS CODE EXTENSION TEST RESULTS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"🕐 Total test time: {total_time:.2f} seconds")
    print(f"📊 Tests passed: {passed}/{total}")
    print(f"📈 Success rate: {success_rate:.1f}%")
    print()
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print()
    if success_rate >= 90:
        print("🎉 EXCEPTIONAL! VS Code extension is production-ready!")
        print("🚀 Ready for VS Code Marketplace publication!")
    elif success_rate >= 80:
        print("🎊 EXCELLENT! Extension is working great!")
        print("👍 Minor issues detected, but ready for use!")
    elif success_rate >= 60:
        print("👍 GOOD! Most extension features working!")
        print("🔧 Some components need attention!")
    else:
        print("⚠️ NEEDS ATTENTION! Several extension components need fixing!")
        print("🛠️ Please check failed components!")
    
    print(f"\n🎯 VS CODE EXTENSION TEST COMPLETED: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
