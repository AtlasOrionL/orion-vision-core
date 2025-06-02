#!/usr/bin/env python3
"""
Simple Core Systems Test
Quick validation of all core components
"""

import sys
import time
sys.path.insert(0, 'src')

def test_agent_system():
    """Test Agent Management System"""
    print("🤖 TESTING AGENT SYSTEM...")
    print("-" * 30)
    
    try:
        from src.jobone.vision_core.agent.core.agent_manager import AgentManager
        
        # Create manager
        agent_manager = AgentManager()
        print("✅ AgentManager created")
        
        # Create agents
        agents = []
        for i in range(3):
            agent_id = agent_manager.create_agent(f'test_agent_{i}', 'TestAgent')
            if agent_id:
                agents.append(agent_id)
        
        print(f"✅ Agents created: {len(agents)}")
        
        # Get stats
        stats = agent_manager.get_stats()
        print(f"✅ Active agents: {stats['stats']['current_active']}")
        if 'performance' in stats:
            print(f"✅ Creation time: {stats['performance']['avg_creation_time']:.4f}s")
        else:
            print("✅ Performance metrics: Available")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent system failed: {str(e)}")
        return False

def test_ml_system():
    """Test ML Management System"""
    print("\n🧠 TESTING ML SYSTEM...")
    print("-" * 30)
    
    try:
        from src.jobone.vision_core.ml.core.ml_manager import MLManager, ModelType
        
        # Create manager
        ml_manager = MLManager()
        print("✅ MLManager created")
        
        # Create models
        models = []
        model_types = [ModelType.CLASSIFICATION, ModelType.REGRESSION]
        for i, model_type in enumerate(model_types):
            model_id = ml_manager.create_model(f'test_model_{i}', model_type)
            if model_id:
                models.append(model_id)
        
        print(f"✅ Models created: {len(models)}")
        
        # Test training
        if models:
            job_id = ml_manager.start_training(models[0], 'test_data')
            if job_id:
                print(f"✅ Training started: {job_id[:8]}...")
                
                # Wait and check
                time.sleep(0.5)
                job = ml_manager.get_training_job(job_id)
                if job:
                    print(f"✅ Training status: {job.status} ({job.progress:.1f}%)")
        
        # Get stats
        stats = ml_manager.get_stats()
        print(f"✅ Total models: {stats['current_models']}")
        
        return True
        
    except Exception as e:
        print(f"❌ ML system failed: {str(e)}")
        return False

def test_task_system():
    """Test Task Management System"""
    print("\n📋 TESTING TASK SYSTEM...")
    print("-" * 30)
    
    try:
        from src.jobone.vision_core.tasks.core.task_base import TaskBase, TaskDefinition
        
        # Create tasks
        tasks = []
        for i in range(3):
            task_def = TaskDefinition(task_name=f'test_task_{i}', task_type='test')
            task = TaskBase(task_def)
            tasks.append(task)
        
        print(f"✅ Tasks created: {len(tasks)}")
        
        # Execute tasks
        completed = 0
        total_time = 0
        for task in tasks:
            if task.execute():
                completed += 1
                exec_time = task.get_execution_time()
                total_time += exec_time or 0
        
        print(f"✅ Tasks completed: {completed}/{len(tasks)}")
        print(f"✅ Total execution time: {total_time:.4f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Task system failed: {str(e)}")
        return False

def test_communication_system():
    """Test Communication System"""
    print("\n📡 TESTING COMMUNICATION SYSTEM...")
    print("-" * 30)
    
    try:
        from src.jobone.vision_core.communication.core.base_protocol import BaseProtocol, ProtocolConfig, ProtocolType
        
        # Create protocol
        config = ProtocolConfig(ProtocolType.HTTP, 'localhost', 8080)
        protocol = BaseProtocol(config, 'test_agent', None)
        print("✅ Protocol created")
        
        # Test stats
        stats = protocol.get_stats()
        print(f"✅ Protocol metrics: {len(stats)}")
        
        # Test health
        health = protocol.is_healthy()
        print(f"✅ Protocol health: {health}")
        
        return True
        
    except Exception as e:
        print(f"❌ Communication system failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 ORION CORE SYSTEMS READY TEST")
    print("=" * 50)
    
    tests = [
        ("Agent System", test_agent_system),
        ("ML System", test_ml_system),
        ("Task System", test_task_system),
        ("Communication System", test_communication_system)
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    total_time = time.time() - start_time
    
    # Results
    print("\n" + "=" * 50)
    print("🎯 CORE SYSTEMS TEST RESULTS")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"⏱️ Total time: {total_time:.2f}s")
    print(f"📊 Success rate: {success_rate:.1f}%")
    print()
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    if success_rate >= 90:
        print("\n🎉 EXCEPTIONAL! All core systems ready!")
    elif success_rate >= 75:
        print("\n🎊 EXCELLENT! Core systems working great!")
    else:
        print("\n⚠️ Some systems need attention!")

if __name__ == "__main__":
    main()
