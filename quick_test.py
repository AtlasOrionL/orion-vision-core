"""
Quick Test Suite for Orion Vision Core
Simple user testing interface

Author: Atlas-orion (Augment Agent)
Date: 2 Haziran 2025
"""

import sys
import os
import requests
import time

# Add src to path
sys.path.insert(0, 'src')

print("🎮 ORION VISION CORE - QUICK TEST SUITE")
print("=" * 50)

def test_ollama():
    """Test Ollama connection"""
    print("\n🔍 TESTING OLLAMA...")
    print("-" * 30)
    
    try:
        # Test connection
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            print("✅ Ollama is running!")
            print(f"📊 Available models: {len(models)}")
            
            for model in models:
                name = model.get('name', 'Unknown')
                size = model.get('size', 0) / (1024*1024*1024)
                print(f"  🤖 {name} ({size:.1f}GB)")
            
            # Test chat
            if models:
                print(f"\n🤖 Testing chat with {models[0]['name']}...")
                
                payload = {
                    "model": models[0]['name'],
                    "prompt": "Merhaba! Test mesajı.",
                    "stream": False
                }
                
                chat_response = requests.post(
                    "http://localhost:11434/api/generate",
                    json=payload,
                    timeout=15
                )
                
                if chat_response.status_code == 200:
                    chat_data = chat_response.json()
                    ai_response = chat_data.get('response', 'No response')
                    duration = chat_data.get('total_duration', 0) / 1e9
                    
                    print(f"📥 AI Response: {ai_response}")
                    print(f"⏱️ Response time: {duration:.2f}s")
                    print("✅ Ollama chat working!")
                else:
                    print("❌ Chat test failed")
            
            return True
        else:
            print(f"❌ Ollama API error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Ollama is not running")
        print("💡 Start with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Ollama test failed: {str(e)}")
        return False

def test_orion_core():
    """Test Orion Core modules"""
    print("\n🚀 TESTING ORION CORE...")
    print("-" * 30)
    
    try:
        # Test imports
        from src.jobone.vision_core.agent.core.agent_manager import AgentManager
        from src.jobone.vision_core.ml.core.ml_manager import MLManager, ModelType
        from src.jobone.vision_core.tasks.core.task_base import TaskBase, TaskDefinition
        
        print("✅ Core modules imported successfully")
        
        # Test Agent Manager
        agent_manager = AgentManager()
        agent_id = agent_manager.create_agent('test_agent', 'TestAgent')
        print(f"✅ Agent created: {agent_id[:8] if agent_id else 'None'}...")
        
        # Test ML Manager
        ml_manager = MLManager()
        model_id = ml_manager.create_model('test_model', ModelType.CLASSIFICATION)
        print(f"✅ Model created: {model_id[:8] if model_id else 'None'}...")
        
        # Test Task System
        task_def = TaskDefinition(task_name='test_task', task_type='test')
        task = TaskBase(task_def)
        result = task.execute()
        print(f"✅ Task executed: {result}")
        
        # Get statistics
        agent_stats = agent_manager.get_stats()
        ml_stats = ml_manager.get_stats()
        
        print(f"📊 Agent stats: {agent_stats['stats']['current_active']} active")
        print(f"📊 ML stats: {ml_stats['current_models']} models")
        
        print("✅ Orion Core working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Orion Core test failed: {str(e)}")
        return False

def test_vs_code_extension():
    """Test VS Code extension files"""
    print("\n🆚 TESTING VS CODE EXTENSION...")
    print("-" * 30)
    
    try:
        # Check extension files
        extension_files = [
            'vs-code-extension/package.json',
            'vs-code-extension/src/extension.ts',
            'vs-code-extension/src/chatProvider.ts',
            'vs-code-extension/src/terminalManager.ts'
        ]
        
        found_files = 0
        for file_path in extension_files:
            if os.path.exists(file_path):
                found_files += 1
                print(f"✅ Found: {file_path}")
            else:
                print(f"❌ Missing: {file_path}")
        
        print(f"📊 Extension files: {found_files}/{len(extension_files)} found")
        
        if found_files >= 3:
            print("✅ VS Code extension files present!")
            return True
        else:
            print("⚠️ Some extension files missing")
            return False
            
    except Exception as e:
        print(f"❌ VS Code extension test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🎯 Choose your test:")
    print("1. Test Ollama (AI Chat)")
    print("2. Test Orion Core (Python System)")
    print("3. Test VS Code Extension (Files)")
    print("4. Test All Systems")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        test_ollama()
    elif choice == "2":
        test_orion_core()
    elif choice == "3":
        test_vs_code_extension()
    elif choice == "4":
        print("\n🚀 TESTING ALL SYSTEMS...")
        print("=" * 50)
        
        results = []
        results.append(("Ollama", test_ollama()))
        results.append(("Orion Core", test_orion_core()))
        results.append(("VS Code Extension", test_vs_code_extension()))
        
        print("\n" + "=" * 50)
        print("🎯 FINAL RESULTS")
        print("=" * 50)
        
        passed = 0
        for name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{name}: {status}")
            if result:
                passed += 1
        
        success_rate = (passed / len(results)) * 100
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT! Your Orion system is working great!")
        elif success_rate >= 60:
            print("👍 GOOD! Most systems working, minor issues detected")
        else:
            print("⚠️ NEEDS ATTENTION! Several systems need fixing")
    
    else:
        print("Invalid choice! Running all tests...")
        main()

if __name__ == "__main__":
    main()
