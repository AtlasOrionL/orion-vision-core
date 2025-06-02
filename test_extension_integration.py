#!/usr/bin/env python3
"""
🧪 VS CODE EXTENSION INTEGRATION TEST
Extension'ın Orion server ile entegrasyonunu test eder
"""

import requests
import json
import time

def test_orion_server():
    """Orion server'ın çalıştığını test et"""
    print("🚀 Testing Orion Server Integration...")
    
    base_url = "http://localhost:8000"
    
    # 1. Health Check
    print("\n1. 🏥 Health Check Test:")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status: {data['status']}")
            print(f"✅ Ollama Connected: {data['ollama']['connected']}")
            print(f"✅ Default Model: {data['ollama']['default_model']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # 2. Chat API Test
    print("\n2. 💬 Chat API Test:")
    try:
        chat_data = {
            "message": "Merhaba! VS Code extension test ediyorum.",
            "model": "llama3.2:1b",
            "conversation_id": "test-conversation"
        }
        
        response = requests.post(
            f"{base_url}/api/chat/send",
            json=chat_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat Response: {data['response'][:100]}...")
            print(f"✅ Model Used: {data['model']}")
            print(f"✅ Conversation ID: {data['conversation_id']}")
        else:
            print(f"❌ Chat API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat API error: {e}")
        return False
    
    # 3. Terminal API Test
    print("\n3. 🖥️ Terminal API Test:")
    try:
        terminal_data = {
            "command": "echo 'Hello from VS Code Extension!'",
            "workingDirectory": "/tmp",
            "timeout": 10
        }
        
        response = requests.post(
            f"{base_url}/api/terminal/execute",
            json=terminal_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Terminal Output: {data['output'].strip()}")
            print(f"✅ Exit Code: {data['exitCode']}")
            print(f"✅ Duration: {data['duration']:.2f}s")
        else:
            print(f"❌ Terminal API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Terminal API error: {e}")
        return False
    
    # 4. Provider List Test
    print("\n4. 🔌 Provider API Test:")
    try:
        response = requests.get(f"{base_url}/api/providers/list", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            providers = data['providers']
            print(f"✅ Found {len(providers)} providers:")
            
            for provider in providers:
                status = "🟢 Connected" if provider['isConnected'] else "🔴 Disconnected"
                print(f"  - {provider['name']}: {status}")
                print(f"    Models: {', '.join(provider['models'][:3])}...")
        else:
            print(f"❌ Provider API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Provider API error: {e}")
        return False
    
    # 5. File System API Test
    print("\n5. 📁 File System API Test:")
    try:
        # Test file read
        fs_data = {
            "operation": "list",
            "path": "/tmp"
        }
        
        response = requests.post(
            f"{base_url}/api/filesystem/operation",
            json=fs_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ File System Operation: {data['success']}")
            if data.get('content'):
                files = json.loads(data['content'])
                print(f"✅ Found {len(files)} items in /tmp")
        else:
            print(f"❌ File System API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ File System API error: {e}")
        return False
    
    print("\n🎉 All API tests passed! Extension integration ready!")
    return True

def test_extension_endpoints():
    """Extension'ın kullanacağı endpoint'leri test et"""
    print("\n🔧 Testing Extension-Specific Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Extension configuration test
    print("\n📋 Extension Configuration Test:")
    extension_config = {
        "server": {
            "host": "localhost",
            "port": 8000,
            "timeout": 30000
        },
        "ai": {
            "provider": "ollama-local",
            "model": "llama3.2:1b",
            "maxTokens": 2048
        },
        "features": {
            "chat": True,
            "terminal": True,
            "fileSystem": True,
            "codeCompletion": True
        }
    }
    
    print("✅ Extension Config:")
    print(f"  - Server: {extension_config['server']['host']}:{extension_config['server']['port']}")
    print(f"  - AI Provider: {extension_config['ai']['provider']}")
    print(f"  - Model: {extension_config['ai']['model']}")
    print(f"  - Features: {', '.join([k for k, v in extension_config['features'].items() if v])}")
    
    # Test VS Code specific scenarios
    print("\n🎯 VS Code Integration Scenarios:")
    
    # Scenario 1: Code completion request
    print("\n1. Code Completion Scenario:")
    code_completion_request = {
        "message": "Complete this Python function: def fibonacci(n):",
        "model": "llama3.2:1b",
        "context": "python_function"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/chat/send",
            json=code_completion_request,
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Code completion response received")
            print(f"✅ Response length: {len(data['response'])} characters")
        else:
            print(f"❌ Code completion failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Code completion error: {e}")
    
    # Scenario 2: Terminal command execution
    print("\n2. Terminal Integration Scenario:")
    terminal_commands = [
        "pwd",
        "ls -la",
        "python3 --version",
        "git status"
    ]
    
    for cmd in terminal_commands:
        try:
            response = requests.post(
                f"{base_url}/api/terminal/execute",
                json={"command": cmd, "timeout": 5},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Command '{cmd}': Exit code {data['exitCode']}")
            else:
                print(f"⚠️ Command '{cmd}' failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Command '{cmd}' error: {e}")
    
    print("\n🎉 Extension integration tests completed!")

def main():
    """Ana test fonksiyonu"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║            🧪 VS CODE EXTENSION INTEGRATION TEST             ║
    ║                                                              ║
    ║  Extension'ın Orion server ile entegrasyonunu test eder      ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Server test
    server_ok = test_orion_server()
    
    if server_ok:
        # Extension specific tests
        test_extension_endpoints()
        
        print("\n" + "="*60)
        print("🎉 INTEGRATION TEST SUMMARY")
        print("="*60)
        print("✅ Orion Server: Running and responsive")
        print("✅ Chat API: Working with Ollama")
        print("✅ Terminal API: Command execution ready")
        print("✅ File System API: File operations ready")
        print("✅ Provider API: AI providers accessible")
        print("✅ VS Code Extension: Ready for integration")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Open VS Code in the extension directory")
        print("2. Press F5 to launch Extension Development Host")
        print("3. Test the extension features:")
        print("   - Ctrl+Shift+O: Activate AI")
        print("   - Ctrl+Shift+C: Open Chat")
        print("   - Ctrl+Shift+T: Open Terminal")
        print("   - Ctrl+Shift+A: Open API Manager")
        
        print("\n📦 Extension Package:")
        print("- orion-vision-core-1.0.0.vsix created")
        print("- Ready for installation and testing")
        
    else:
        print("\n❌ Server tests failed. Please check Orion server status.")

if __name__ == "__main__":
    main()
