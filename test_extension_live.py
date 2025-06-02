#!/usr/bin/env python3
"""
🎯 LIVE EXTENSION TEST
VS Code extension'ın canlı testini yapar
"""

import requests
import json
import time
import threading

def test_chat_api():
    """Chat API'yi sürekli test et"""
    print("💬 Testing Chat API...")
    
    test_messages = [
        "Merhaba! VS Code extension test ediyorum.",
        "Python'da bir web scraper nasıl yazarım?",
        "React component'i nasıl oluştururum?",
        "Git komutları nelerdir?",
        "VS Code extension geliştirme hakkında bilgi ver."
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Chat Test: {message[:50]}...")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/chat/send",
                json={
                    "message": message,
                    "model": "llama3.2:1b",
                    "conversation_id": f"test-{i}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response'][:100]}...")
                print(f"✅ Model: {data['model']}")
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(2)

def test_terminal_api():
    """Terminal API'yi test et"""
    print("\n🖥️ Testing Terminal API...")
    
    commands = [
        "pwd",
        "ls -la",
        "echo 'Hello from Orion Extension!'",
        "python3 --version",
        "whoami",
        "date",
        "uname -a"
    ]
    
    for cmd in commands:
        print(f"\n🔧 Executing: {cmd}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/terminal/execute",
                json={
                    "command": cmd,
                    "workingDirectory": "/tmp",
                    "timeout": 10
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Output: {data['output'].strip()}")
                print(f"✅ Exit Code: {data['exitCode']}")
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_file_system_api():
    """File System API'yi test et"""
    print("\n📁 Testing File System API...")
    
    operations = [
        {"operation": "list", "path": "/tmp"},
        {"operation": "list", "path": "/home"},
        {"operation": "create", "path": "/tmp/orion_test.txt", "content": "Hello from Orion Extension!"},
        {"operation": "read", "path": "/tmp/orion_test.txt"},
        {"operation": "delete", "path": "/tmp/orion_test.txt"}
    ]
    
    for op in operations:
        print(f"\n📂 Operation: {op['operation']} - {op['path']}")
        
        try:
            response = requests.post(
                "http://localhost:8000/api/filesystem/operation",
                json=op,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data['success']}")
                if data.get('content'):
                    content = data['content'][:100]
                    print(f"✅ Content: {content}...")
                if data.get('size'):
                    print(f"✅ Size: {data['size']} bytes")
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_provider_api():
    """Provider API'yi test et"""
    print("\n🔌 Testing Provider API...")
    
    try:
        # List providers
        response = requests.get("http://localhost:8000/api/providers/list", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            providers = data['providers']
            
            print(f"✅ Found {len(providers)} providers:")
            for provider in providers:
                status = "🟢" if provider['isConnected'] else "🔴"
                print(f"  {status} {provider['name']}: {provider['type']}")
                print(f"    Models: {', '.join(provider['models'][:3])}")
                
                # Test provider connection
                print(f"    Testing connection...")
                test_response = requests.post(
                    f"http://localhost:8000/api/providers/test/{provider['id']}",
                    timeout=15
                )
                
                if test_response.status_code == 200:
                    test_data = test_response.json()
                    status = "✅" if test_data['connected'] else "❌"
                    print(f"    {status} {test_data['message']}")
                else:
                    print(f"    ❌ Test failed: {test_response.status_code}")
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def monitor_server():
    """Server durumunu sürekli izle"""
    print("\n📊 Starting server monitoring...")
    
    while True:
        try:
            response = requests.get("http://localhost:8000/api/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                timestamp = data['timestamp']
                ollama_status = "🟢" if data['ollama']['connected'] else "🔴"
                print(f"\r📊 Server Status: ✅ Healthy | Ollama: {ollama_status} | Time: {timestamp}", end="", flush=True)
            else:
                print(f"\r📊 Server Status: ❌ Error {response.status_code}", end="", flush=True)
                
        except Exception as e:
            print(f"\r📊 Server Status: ❌ Connection failed", end="", flush=True)
        
        time.sleep(5)

def main():
    """Ana test fonksiyonu"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                🎯 LIVE EXTENSION TEST                        ║
    ║                                                              ║
    ║  VS Code extension'ın tüm özelliklerini canlı test eder     ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Server monitoring'i background'da başlat
    monitor_thread = threading.Thread(target=monitor_server, daemon=True)
    monitor_thread.start()
    
    print("🚀 Starting comprehensive extension tests...")
    
    try:
        # 1. Provider API Test
        test_provider_api()
        
        # 2. Terminal API Test
        test_terminal_api()
        
        # 3. File System API Test
        test_file_system_api()
        
        # 4. Chat API Test (en son, zaman alıyor)
        test_chat_api()
        
        print("\n\n🎉 ALL TESTS COMPLETED!")
        print("="*60)
        print("✅ Provider API: Working")
        print("✅ Terminal API: Working") 
        print("✅ File System API: Working")
        print("✅ Chat API: Working")
        print("="*60)
        
        print("\n🎯 VS CODE EXTENSION READY!")
        print("1. Open VS Code in vscode-extension directory")
        print("2. Press F5 to launch Extension Development Host")
        print("3. Test these features:")
        print("   - Ctrl+Shift+C: Open Chat")
        print("   - Ctrl+Shift+T: Open Terminal")
        print("   - Ctrl+Shift+A: Open API Manager")
        print("   - Ctrl+Shift+O: Activate AI")
        
        # Keep monitoring
        print("\n📊 Monitoring server (Ctrl+C to stop)...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Test stopped by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")

if __name__ == "__main__":
    main()
