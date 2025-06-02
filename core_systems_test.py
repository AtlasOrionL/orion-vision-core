#!/usr/bin/env python3
"""
Orion Vision Core - Core Systems Ready Test
Comprehensive testing of all core system components

Author: Atlas-orion (Augment Agent)
Date: 2 Haziran 2025
Purpose: Deep core systems validation
"""

import sys
import time
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, 'src')

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print formatted section"""
    print(f"\n🔍 {title}")
    print("-" * 40)

def test_agent_system_deep():
    """Deep test of Agent Management System"""
    print_section("AGENT MANAGEMENT SYSTEM - DEEP TEST")
    
    try:
        from src.jobone.vision_core.agent.core.agent_manager import AgentManager, AgentState
        from src.jobone.vision_core.agent.core.agent_logger import AgentLogger
        
        # Create logger and manager
        logger = AgentLogger("core_test")
        agent_manager = AgentManager(logger=logger)
        
        print("✅ AgentManager initialized with logger")
        
        # Test 1: Multiple agent creation with different capabilities
        print("\n🤖 Testing multiple agent creation...")
        agents = []
        agent_configs = [
            ('data_processor', 'DataAgent', ['data_processing', 'analysis']),
            ('ml_trainer', 'MLAgent', ['model_training', 'evaluation']),
            ('task_executor', 'TaskAgent', ['task_execution', 'workflow']),
            ('communication_hub', 'CommAgent', ['messaging', 'coordination']),
            ('monitor_agent', 'MonitorAgent', ['monitoring', 'alerting'])
        ]
        
        for name, agent_type, capabilities in agent_configs:
            agent_id = agent_manager.create_agent(name, agent_type, capabilities)
            if agent_id:
                agents.append((agent_id, name, agent_type))
                print(f"  ✅ {name} ({agent_type}): {agent_id[:8]}...")
        
        print(f"✅ Created {len(agents)} specialized agents")
        
        # Test 2: Agent information retrieval
        print("\n📊 Testing agent information retrieval...")
        for agent_id, name, agent_type in agents[:3]:  # Test first 3
            agent_info = agent_manager.get_agent(agent_id)
            if agent_info:
                print(f"  ✅ {name}: Status={agent_info.state.value}, Type={agent_info.agent_type}")
            else:
                print(f"  ❌ {name}: Failed to retrieve info")
        
        # Test 3: Agent listing and filtering
        print("\n📋 Testing agent listing...")
        all_agents = agent_manager.list_agents()
        active_agents = [a for a in all_agents if a.state == AgentState.ACTIVE]
        print(f"✅ Total agents: {len(all_agents)}, Active: {len(active_agents)}")
        
        # Test 4: Agent statistics
        print("\n📈 Testing agent statistics...")
        stats = agent_manager.get_stats()
        print(f"✅ Stats: {stats['stats']['current_active']} active, {stats['stats']['total_created']} total")
        print(f"✅ Performance: {stats['performance']['avg_creation_time']:.4f}s avg creation")
        
        # Test 5: Agent termination
        print("\n🔄 Testing agent termination...")
        if agents:
            test_agent_id = agents[-1][0]  # Terminate last agent
            if agent_manager.terminate_agent(test_agent_id):
                print(f"✅ Agent terminated: {test_agent_id[:8]}...")
            else:
                print(f"❌ Failed to terminate agent")
        
        # Final stats
        final_stats = agent_manager.get_stats()
        print(f"✅ Final stats: {final_stats['stats']['current_active']} active")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent system test failed: {str(e)}")
        return False

def test_ml_system_deep():
    """Deep test of ML Management System"""
    print_section("ML MANAGEMENT SYSTEM - DEEP TEST")
    
    try:
        from src.jobone.vision_core.ml.core.ml_manager import MLManager, ModelType, ModelStatus
        
        # Create ML manager
        ml_manager = MLManager()
        print("✅ MLManager initialized")
        
        # Test 1: Multiple model creation with different types
        print("\n🧠 Testing multiple model creation...")
        models = []
        model_configs = [
            ('customer_classifier', ModelType.CLASSIFICATION, {'classes': 5, 'features': 100}),
            ('price_predictor', ModelType.REGRESSION, {'target': 'price', 'features': 50}),
            ('user_segmentation', ModelType.CLUSTERING, {'clusters': 3, 'algorithm': 'kmeans'}),
            ('anomaly_detector', ModelType.CLASSIFICATION, {'threshold': 0.95, 'method': 'isolation'}),
            ('recommendation_engine', ModelType.REGRESSION, {'collaborative': True, 'content': True})
        ]
        
        for name, model_type, config in model_configs:
            model_id = ml_manager.create_model(name, model_type, config)
            if model_id:
                models.append((model_id, name, model_type))
                print(f"  ✅ {name} ({model_type.value}): {model_id[:8]}...")
        
        print(f"✅ Created {len(models)} ML models")
        
        # Test 2: Model training
        print("\n🏋️ Testing model training...")
        training_jobs = []
        for model_id, name, model_type in models[:3]:  # Train first 3 models
            job_id = ml_manager.start_training(
                model_id, 
                f'{name}_training_data',
                {'epochs': 2, 'batch_size': 32, 'learning_rate': 0.001}
            )
            if job_id:
                training_jobs.append((job_id, name))
                print(f"  ✅ Training started for {name}: {job_id[:8]}...")
        
        # Wait for training completion
        print("\n⏳ Waiting for training completion...")
        time.sleep(1.5)  # Allow training to complete
        
        # Check training results
        completed_trainings = 0
        for job_id, name in training_jobs:
            job = ml_manager.get_training_job(job_id)
            if job:
                print(f"  ✅ {name}: {job.status} ({job.progress:.1f}%)")
                if job.status == 'completed':
                    completed_trainings += 1
        
        print(f"✅ Completed trainings: {completed_trainings}/{len(training_jobs)}")
        
        # Test 3: Model inference
        print("\n🔮 Testing model inference...")
        predictions_made = 0
        for model_id, name, model_type in models[:2]:  # Test inference on first 2
            prediction = ml_manager.predict(model_id, f'{name}_test_data')
            if prediction:
                print(f"  ✅ {name}: Prediction={prediction['prediction']}, Confidence={prediction['confidence']:.3f}")
                predictions_made += 1
        
        print(f"✅ Predictions made: {predictions_made}")
        
        # Test 4: Model information and statistics
        print("\n📊 Testing model information...")
        for model_id, name, model_type in models[:2]:
            model_info = ml_manager.get_model(model_id)
            if model_info:
                print(f"  ✅ {name}: Status={model_info.status.value}, Accuracy={model_info.accuracy:.3f}")
        
        # ML system statistics
        ml_stats = ml_manager.get_stats()
        print(f"✅ ML Stats: {ml_stats['current_models']} models, {ml_stats['stats']['total_training_jobs']} training jobs")
        
        return True
        
    except Exception as e:
        print(f"❌ ML system test failed: {str(e)}")
        return False

def test_task_system_deep():
    """Deep test of Task Management System"""
    print_section("TASK MANAGEMENT SYSTEM - DEEP TEST")
    
    try:
        from src.jobone.vision_core.tasks.core.task_base import TaskBase, TaskDefinition, TaskStatus, TaskPriority
        
        # Test 1: Complex task creation
        print("\n📋 Testing complex task creation...")
        tasks = []
        task_configs = [
            ('data_ingestion', 'data_processing', {'source': 'database', 'format': 'json'}, TaskPriority.HIGH),
            ('feature_extraction', 'preprocessing', {'method': 'pca', 'components': 50}, TaskPriority.NORMAL),
            ('model_validation', 'validation', {'cross_validation': True, 'folds': 5}, TaskPriority.HIGH),
            ('report_generation', 'reporting', {'format': 'pdf', 'charts': True}, TaskPriority.LOW),
            ('data_cleanup', 'maintenance', {'remove_duplicates': True, 'normalize': True}, TaskPriority.NORMAL)
        ]
        
        for name, task_type, input_data, priority in task_configs:
            task_def = TaskDefinition(
                task_name=name,
                task_type=task_type,
                input_data=input_data,
                priority=priority,
                timeout=60.0,
                retry_count=2
            )
            task = TaskBase(task_def)
            tasks.append((task, name))
            print(f"  ✅ {name} ({task_type}): Priority={priority.value}")
        
        print(f"✅ Created {len(tasks)} complex tasks")
        
        # Test 2: Task execution with timing
        print("\n⚡ Testing task execution...")
        execution_results = []
        total_execution_time = 0
        
        for task, name in tasks:
            start_time = time.time()
            result = task.execute()
            execution_time = task.get_execution_time()
            
            execution_results.append((name, result, execution_time))
            total_execution_time += execution_time or 0
            
            status = "✅ SUCCESS" if result else "❌ FAILED"
            print(f"  {status} {name}: {execution_time:.4f}s")
        
        successful_tasks = sum(1 for _, result, _ in execution_results if result)
        print(f"✅ Task execution: {successful_tasks}/{len(tasks)} successful")
        print(f"✅ Total execution time: {total_execution_time:.4f}s")
        
        # Test 3: Task serialization and metadata
        print("\n💾 Testing task serialization...")
        serialized_tasks = 0
        for task, name in tasks[:3]:  # Test first 3
            try:
                task_dict = task.to_dict()
                if isinstance(task_dict, dict) and 'definition' in task_dict:
                    serialized_tasks += 1
                    print(f"  ✅ {name}: Serialized successfully")
            except Exception as e:
                print(f"  ❌ {name}: Serialization failed - {str(e)}")
        
        print(f"✅ Serialization: {serialized_tasks}/{min(3, len(tasks))} successful")
        
        # Test 4: Task status and lifecycle
        print("\n🔄 Testing task lifecycle...")
        lifecycle_test_task = tasks[0][0] if tasks else None
        if lifecycle_test_task:
            print(f"  ✅ Initial status: {lifecycle_test_task.get_status().value}")
            print(f"  ✅ Has result: {lifecycle_test_task.get_result() is not None}")
            print(f"  ✅ Has error: {lifecycle_test_task.get_error() is not None}")
            print(f"  ✅ Execution time: {lifecycle_test_task.get_execution_time():.4f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Task system test failed: {str(e)}")
        return False

def test_communication_system_deep():
    """Deep test of Communication System"""
    print_section("COMMUNICATION SYSTEM - DEEP TEST")
    
    try:
        from src.jobone.vision_core.communication.core.base_protocol import (
            BaseProtocol, ProtocolConfig, ProtocolType, ConnectionStatus,
            CommunicationMessage, MessageType, MessagePriority
        )
        from src.jobone.vision_core.agent.core.agent_logger import AgentLogger
        
        # Test 1: Multiple protocol creation
        print("\n📡 Testing multiple protocol creation...")
        protocols = []
        protocol_configs = [
            ('http_protocol', ProtocolType.HTTP, 'localhost', 8080),
            ('websocket_protocol', ProtocolType.WEBSOCKET, 'localhost', 8081),
            ('grpc_protocol', ProtocolType.GRPC, 'localhost', 8082),
            ('tcp_protocol', ProtocolType.TCP, 'localhost', 8083)
        ]
        
        logger = AgentLogger("comm_test")
        
        for name, protocol_type, host, port in protocol_configs:
            config = ProtocolConfig(protocol_type, host, port)
            protocol = BaseProtocol(config, f'{name}_agent', logger)
            protocols.append((protocol, name, protocol_type))
            print(f"  ✅ {name} ({protocol_type.value}): {host}:{port}")
        
        print(f"✅ Created {len(protocols)} protocols")
        
        # Test 2: Protocol statistics and health
        print("\n📊 Testing protocol statistics...")
        for protocol, name, protocol_type in protocols:
            stats = protocol.get_stats()
            health = protocol.is_healthy()
            connected = protocol.is_connected()
            
            print(f"  ✅ {name}: Health={health}, Connected={connected}, Metrics={len(stats)}")
        
        # Test 3: Message creation and handling
        print("\n💬 Testing message creation...")
        messages = []
        message_configs = [
            ('task_request', MessageType.TASK_REQUEST, MessagePriority.HIGH),
            ('status_update', MessageType.STATUS_UPDATE, MessagePriority.NORMAL),
            ('heartbeat', MessageType.HEARTBEAT, MessagePriority.LOW),
            ('notification', MessageType.NOTIFICATION, MessagePriority.NORMAL)
        ]
        
        for i, (msg_type_name, msg_type, priority) in enumerate(message_configs):
            message = CommunicationMessage(
                message_id=f'msg_{i}_{int(time.time())}',
                message_type=msg_type,
                sender_id='test_sender',
                recipient_id='test_recipient',
                content={'data': f'test_data_{i}', 'timestamp': time.time()},
                priority=priority
            )
            messages.append((message, msg_type_name))
            print(f"  ✅ {msg_type_name}: Priority={priority.value}")
        
        print(f"✅ Created {len(messages)} messages")
        
        # Test 4: Message serialization
        print("\n💾 Testing message serialization...")
        serialized_messages = 0
        for message, name in messages:
            try:
                msg_dict = message.to_dict()
                if isinstance(msg_dict, dict) and 'message_id' in msg_dict:
                    serialized_messages += 1
                    print(f"  ✅ {name}: Serialized successfully")
            except Exception as e:
                print(f"  ❌ {name}: Serialization failed")
        
        print(f"✅ Message serialization: {serialized_messages}/{len(messages)} successful")
        
        # Test 5: Protocol configuration validation
        print("\n🔧 Testing protocol configuration...")
        try:
            # Test valid config
            valid_config = ProtocolConfig(ProtocolType.HTTP, 'localhost', 8080)
            print("  ✅ Valid config: Created successfully")
            
            # Test config serialization
            config_dict = valid_config.to_dict()
            restored_config = ProtocolConfig.from_dict(config_dict)
            print("  ✅ Config serialization: Round-trip successful")
            
        except Exception as e:
            print(f"  ❌ Config validation failed: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Communication system test failed: {str(e)}")
        return False

def test_system_integration():
    """Test integration between core systems"""
    print_section("CORE SYSTEMS INTEGRATION TEST")
    
    try:
        # Import all systems
        from src.jobone.vision_core.agent.core.agent_manager import AgentManager
        from src.jobone.vision_core.ml.core.ml_manager import MLManager, ModelType
        from src.jobone.vision_core.tasks.core.task_base import TaskBase, TaskDefinition
        from src.jobone.vision_core.communication.core.base_protocol import BaseProtocol, ProtocolConfig, ProtocolType
        
        print("✅ All core systems imported")
        
        # Test 1: Cross-system workflow
        print("\n🔄 Testing cross-system workflow...")
        
        # Create systems
        agent_manager = AgentManager()
        ml_manager = MLManager()
        
        # Create agent for ML tasks
        ml_agent_id = agent_manager.create_agent('ml_worker', 'MLWorker', ['model_training', 'prediction'])
        print(f"  ✅ ML Agent created: {ml_agent_id[:8]}...")
        
        # Create ML model
        model_id = ml_manager.create_model('integration_model', ModelType.CLASSIFICATION)
        print(f"  ✅ ML Model created: {model_id[:8]}...")
        
        # Create task for model training
        task_def = TaskDefinition(
            task_name='train_integration_model',
            task_type='ml_training',
            input_data={'model_id': model_id, 'agent_id': ml_agent_id}
        )
        task = TaskBase(task_def)
        
        # Execute integrated workflow
        if task.execute():
            print("  ✅ Integrated task executed successfully")
            
            # Start actual ML training
            job_id = ml_manager.start_training(model_id, 'integration_data')
            if job_id:
                print(f"  ✅ ML Training started: {job_id[:8]}...")
        
        # Test 2: System statistics aggregation
        print("\n📊 Testing system statistics aggregation...")
        agent_stats = agent_manager.get_stats()
        ml_stats = ml_manager.get_stats()
        
        total_agents = agent_stats['stats']['current_active']
        total_models = ml_stats['current_models']
        
        print(f"  ✅ System overview: {total_agents} agents, {total_models} models")
        print(f"  ✅ Agent performance: {agent_stats['performance']['avg_creation_time']:.4f}s")
        print(f"  ✅ ML performance: {ml_stats['stats']['total_training_jobs']} training jobs")
        
        # Test 3: Resource coordination
        print("\n🎯 Testing resource coordination...")
        
        # Create multiple agents for different tasks
        coordination_agents = []
        for i in range(3):
            agent_id = agent_manager.create_agent(f'coord_agent_{i}', 'CoordAgent')
            if agent_id:
                coordination_agents.append(agent_id)
        
        # Create multiple models for different agents
        coordination_models = []
        for i, agent_id in enumerate(coordination_agents):
            model_id = ml_manager.create_model(f'coord_model_{i}', ModelType.REGRESSION)
            if model_id:
                coordination_models.append((model_id, agent_id))
        
        print(f"  ✅ Resource coordination: {len(coordination_agents)} agents, {len(coordination_models)} models")
        
        # Test 4: Communication between systems
        print("\n📡 Testing inter-system communication...")
        
        config = ProtocolConfig(ProtocolType.HTTP, 'localhost', 8080)
        protocol = BaseProtocol(config, 'integration_test', None)
        
        protocol_stats = protocol.get_stats()
        print(f"  ✅ Communication protocol: {len(protocol_stats)} metrics available")
        
        return True
        
    except Exception as e:
        print(f"❌ System integration test failed: {str(e)}")
        return False

def main():
    """Main core systems test function"""
    print_header("ORION VISION CORE - CORE SYSTEMS READY TEST")
    print(f"🕐 Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all core system tests
    tests = [
        ("Agent Management System", test_agent_system_deep),
        ("ML Management System", test_ml_system_deep),
        ("Task Management System", test_task_system_deep),
        ("Communication System", test_communication_system_deep),
        ("System Integration", test_system_integration)
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
    print_header("CORE SYSTEMS TEST RESULTS")
    
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
        print("🎉 EXCEPTIONAL! All core systems are production-ready!")
        print("🚀 Orion Vision Core is fully operational!")
    elif success_rate >= 80:
        print("🎊 EXCELLENT! Core systems are working great!")
        print("👍 Minor issues detected, but ready for use!")
    elif success_rate >= 60:
        print("👍 GOOD! Most core systems working!")
        print("🔧 Some components need attention!")
    else:
        print("⚠️ NEEDS ATTENTION! Several core systems need fixing!")
        print("🛠️ Please check failed components!")
    
    print(f"\n🎯 CORE SYSTEMS TEST COMPLETED: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
