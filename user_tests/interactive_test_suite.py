"""
Interactive Test Suite for Orion Vision Core
User-friendly testing interface for all system components

Author: Atlas-orion (Augment Agent)
Date: 2 Haziran 2025
Purpose: User testing and system validation
"""

import sys
import os
import time
import json
import requests
from typing import Dict, Any, Optional

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_path)

# Import Orion modules
from src.jobone.vision_core.agent.core.agent_manager import AgentManager
from src.jobone.vision_core.ml.core.ml_manager import MLManager, ModelType
from src.jobone.vision_core.tasks.core.task_base import TaskBase, TaskDefinition
from src.jobone.vision_core.communication.core.base_protocol import BaseProtocol, ProtocolConfig, ProtocolType
from src.jobone.vision_core.agent.core.agent_logger import AgentLogger


class OrionTestSuite:
    """Interactive test suite for Orion Vision Core"""
    
    def __init__(self):
        """Initialize test suite"""
        self.logger = AgentLogger("user_test")
        self.agent_manager = None
        self.ml_manager = None
        self.protocol = None
        
        print("🎮 ORION VISION CORE - INTERACTIVE TEST SUITE")
        print("=" * 60)
        print("🎯 Test your Orion system with easy interactive tests!")
        print()
    
    def test_ollama_connection(self) -> bool:
        """Test Ollama connection and available models"""
        print("🔍 TESTING OLLAMA CONNECTION...")
        print("-" * 40)
        
        try:
            # Test Ollama API
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                print(f"✅ Ollama is running!")
                print(f"📊 Available models: {len(models)}")
                
                for model in models:
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0) / (1024*1024*1024)  # Convert to GB
                    print(f"  🤖 {name} ({size:.1f}GB)")
                
                return True
            else:
                print(f"❌ Ollama API error: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Ollama is not running or not accessible")
            print("💡 Start Ollama with: ollama serve")
            return False
        except Exception as e:
            print(f"❌ Ollama test failed: {str(e)}")
            return False
    
    def test_ollama_chat(self, model_name: str = "llama3.2:1b") -> bool:
        """Test Ollama chat functionality"""
        print(f"🤖 TESTING OLLAMA CHAT WITH {model_name}...")
        print("-" * 40)
        
        try:
            prompt = "Merhaba! Orion Vision Core sistemini test ediyoruz. Türkçe kısa bir yanıt ver."
            
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False
            }
            
            print(f"📤 Sending: {prompt}")
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', 'No response')
                
                print(f"📥 AI Response: {ai_response}")
                print(f"⏱️ Generation time: {data.get('total_duration', 0) / 1e9:.2f}s")
                
                return True
            else:
                print(f"❌ Chat failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Chat test failed: {str(e)}")
            return False
    
    def test_agent_system(self) -> bool:
        """Test Orion Agent Management System"""
        print("🤖 TESTING AGENT MANAGEMENT SYSTEM...")
        print("-" * 40)
        
        try:
            # Initialize Agent Manager
            self.agent_manager = AgentManager(logger=self.logger)
            print("✅ AgentManager initialized")
            
            # Create test agents
            agents = []
            for i in range(3):
                agent_id = self.agent_manager.create_agent(
                    f'test_agent_{i}', 
                    'UserTestAgent',
                    ['chat', 'analysis', 'coding']
                )
                if agent_id:
                    agents.append(agent_id)
                    print(f"✅ Agent {i+1} created: {agent_id[:8]}...")
            
            # Get agent statistics
            stats = self.agent_manager.get_stats()
            print(f"📊 Agent stats: {stats['stats']['current_active']} active, {stats['stats']['total_created']} total")
            
            # List all agents
            agent_list = self.agent_manager.list_agents()
            print(f"📋 Agent list: {len(agent_list)} agents found")
            
            return len(agents) >= 2
            
        except Exception as e:
            print(f"❌ Agent system test failed: {str(e)}")
            return False
    
    def test_ml_system(self) -> bool:
        """Test Orion ML Management System"""
        print("🧠 TESTING ML MANAGEMENT SYSTEM...")
        print("-" * 40)
        
        try:
            # Initialize ML Manager
            self.ml_manager = MLManager(logger=self.logger)
            print("✅ MLManager initialized")
            
            # Create test models
            models = []
            model_types = [ModelType.CLASSIFICATION, ModelType.REGRESSION, ModelType.CLUSTERING]
            
            for i, model_type in enumerate(model_types):
                model_id = self.ml_manager.create_model(
                    f'user_test_model_{i}',
                    model_type,
                    {'test_param': f'value_{i}'}
                )
                if model_id:
                    models.append(model_id)
                    print(f"✅ {model_type.value} model created: {model_id[:8]}...")
            
            # Test training
            if models:
                job_id = self.ml_manager.start_training(
                    models[0], 
                    'user_test_data',
                    {'epochs': 2, 'batch_size': 32}
                )
                if job_id:
                    print(f"✅ Training started: {job_id[:8]}...")
                    
                    # Wait for training
                    time.sleep(1)
                    
                    # Check training status
                    job = self.ml_manager.get_training_job(job_id)
                    if job:
                        print(f"📊 Training status: {job.status}, Progress: {job.progress:.1f}%")
            
            # Get ML statistics
            stats = self.ml_manager.get_stats()
            print(f"📊 ML stats: {stats['current_models']} models, {stats['stats']['total_training_jobs']} training jobs")
            
            return len(models) >= 2
            
        except Exception as e:
            print(f"❌ ML system test failed: {str(e)}")
            return False
    
    def test_task_system(self) -> bool:
        """Test Orion Task Management System"""
        print("📋 TESTING TASK MANAGEMENT SYSTEM...")
        print("-" * 40)
        
        try:
            # Create test tasks
            tasks = []
            task_types = ['data_processing', 'model_training', 'analysis', 'reporting']
            
            for i, task_type in enumerate(task_types):
                task_def = TaskDefinition(
                    task_name=f'user_test_task_{i}',
                    task_type=task_type,
                    input_data={'test_input': f'data_{i}'},
                    timeout=30.0
                )
                task = TaskBase(task_def)
                tasks.append(task)
                print(f"✅ Task created: {task_def.task_name}")
            
            # Execute tasks
            completed = 0
            for task in tasks:
                if task.execute():
                    completed += 1
                    print(f"✅ Task completed: {task.definition.task_name} in {task.get_execution_time():.4f}s")
                else:
                    print(f"❌ Task failed: {task.definition.task_name}")
            
            print(f"📊 Task results: {completed}/{len(tasks)} completed successfully")
            
            return completed >= 3
            
        except Exception as e:
            print(f"❌ Task system test failed: {str(e)}")
            return False
    
    def test_communication_system(self) -> bool:
        """Test Orion Communication System"""
        print("📡 TESTING COMMUNICATION SYSTEM...")
        print("-" * 40)
        
        try:
            # Initialize Protocol
            config = ProtocolConfig(ProtocolType.HTTP, 'localhost', 8080)
            self.protocol = BaseProtocol(config, 'user_test_agent', self.logger)
            print("✅ Protocol initialized")
            
            # Test protocol statistics
            stats = self.protocol.get_stats()
            print(f"📊 Protocol stats: {stats['connection_attempts']} attempts, {stats['messages_sent']} sent")
            
            # Test protocol health
            health = self.protocol.is_healthy()
            print(f"🏥 Protocol health: {'Healthy' if health else 'Unhealthy'}")
            
            return True
            
        except Exception as e:
            print(f"❌ Communication system test failed: {str(e)}")
            return False
    
    def run_full_test_suite(self) -> Dict[str, bool]:
        """Run complete test suite"""
        print("🚀 RUNNING FULL ORION TEST SUITE...")
        print("=" * 60)
        
        tests = [
            ("Ollama Connection", self.test_ollama_connection),
            ("Ollama Chat", self.test_ollama_chat),
            ("Agent System", self.test_agent_system),
            ("ML System", self.test_ml_system),
            ("Task System", self.test_task_system),
            ("Communication System", self.test_communication_system)
        ]
        
        results = {}
        passed = 0
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name} Test...")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                results[test_name] = False
                print(f"❌ {test_name}: ERROR - {str(e)}")
            
            print()
        
        # Final results
        total = len(tests)
        success_rate = (passed / total) * 100
        
        print("=" * 60)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {passed}/{total}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 EXCELLENT! Your Orion system is working great!")
        elif success_rate >= 60:
            print("👍 GOOD! Most systems are working, minor issues detected")
        else:
            print("⚠️ NEEDS ATTENTION! Several systems need fixing")
        
        return results


def main():
    """Main interactive test function"""
    test_suite = OrionTestSuite()
    
    print("Choose your test:")
    print("1. Quick Ollama Test")
    print("2. Full System Test")
    print("3. Individual Component Tests")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🔍 QUICK OLLAMA TEST")
        print("=" * 30)
        test_suite.test_ollama_connection()
        if input("\nTest chat? (y/n): ").lower() == 'y':
            test_suite.test_ollama_chat()
    
    elif choice == "2":
        print("\n🚀 FULL SYSTEM TEST")
        print("=" * 30)
        test_suite.run_full_test_suite()
    
    elif choice == "3":
        print("\n🧪 INDIVIDUAL COMPONENT TESTS")
        print("=" * 30)
        components = [
            ("Ollama", test_suite.test_ollama_connection),
            ("Agents", test_suite.test_agent_system),
            ("ML", test_suite.test_ml_system),
            ("Tasks", test_suite.test_task_system),
            ("Communication", test_suite.test_communication_system)
        ]
        
        for i, (name, _) in enumerate(components, 1):
            print(f"{i}. {name}")
        
        comp_choice = input("\nChoose component (1-5): ").strip()
        try:
            idx = int(comp_choice) - 1
            if 0 <= idx < len(components):
                name, test_func = components[idx]
                print(f"\n🧪 Testing {name}...")
                test_func()
            else:
                print("Invalid choice!")
        except ValueError:
            print("Invalid choice!")
    
    else:
        print("Invalid choice! Running full test suite...")
        test_suite.run_full_test_suite()


if __name__ == "__main__":
    main()
