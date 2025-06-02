#!/usr/bin/env python3
"""
Task Orchestration Demo - Sprint 4.2
Orion Vision Core - Distributed Agent Coordination

Bu demo, Distributed Task Orchestration sisteminin tüm özelliklerini
gösterir ve test eder.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import asyncio
import time
import random
import sys
import os
from typing import List, Dict, Any

# Orion modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from jobone.vision_core.service_discovery import ServiceDiscoveryManager, LoadBalancingStrategy
from jobone.vision_core.task_orchestration import (
    DistributedTaskOrchestrationManager,
    TaskDefinition,
    TaskPriority,
    ConsensusType
)


class MockAgent:
    """Mock Agent - Task Orchestration test için"""
    
    def __init__(self, agent_id: str, capabilities: List[str] = None):
        self.agent_id = agent_id
        self.capabilities = capabilities or []
        self.service_id = None
        self.running = False
        
    async def start(self, discovery_manager: ServiceDiscoveryManager):
        """Agent'ı başlat ve service discovery'ye kaydet"""
        if self.running:
            return
        
        self.running = True
        
        # Service'i kaydet
        self.service_id = discovery_manager.register_agent_service(
            agent_id=self.agent_id,
            service_name=f"agent_{self.agent_id}",
            host="localhost",
            port=random.randint(8000, 9000),
            capabilities=self.capabilities,
            metadata={"type": "mock_agent", "version": "1.0.0"},
            tags=["test", "orchestration"]
        )
        
        print(f"🤖 Mock Agent {self.agent_id} started with service ID: {self.service_id}")
    
    async def stop(self, discovery_manager: ServiceDiscoveryManager):
        """Agent'ı durdur ve service discovery'den çıkar"""
        if not self.running:
            return
        
        self.running = False
        
        if self.service_id:
            discovery_manager.unregister_agent_service(self.service_id)
            print(f"🛑 Mock Agent {self.agent_id} stopped and unregistered")


async def setup_test_environment():
    """Test ortamını hazırla"""
    print("\n" + "="*70)
    print("🔧 SETTING UP TEST ENVIRONMENT")
    print("="*70)
    
    # Service Discovery Manager oluştur
    discovery_manager = ServiceDiscoveryManager(
        registry_id="orchestration_demo_registry",
        health_check_interval=15.0,
        cleanup_interval=30.0,
        load_balancing_strategy=LoadBalancingStrategy.LEAST_CONNECTIONS
    )
    
    # Discovery manager'ı başlat
    await discovery_manager.start()
    
    # Mock agent'ları oluştur
    agents = [
        MockAgent("calc_agent_001", ["calculation", "math", "statistics"]),
        MockAgent("data_agent_002", ["data_processing", "analytics", "reporting"]),
        MockAgent("file_agent_003", ["file_handling", "storage", "backup"]),
        MockAgent("ml_agent_004", ["machine_learning", "prediction", "classification"]),
        MockAgent("comm_agent_005", ["communication", "messaging", "notification"])
    ]
    
    # Agent'ları başlat
    print("\n📝 Starting mock agents...")
    for agent in agents:
        await agent.start(discovery_manager)
        await asyncio.sleep(0.3)  # Staggered startup
    
    # Orchestration Manager oluştur
    orchestration_manager = DistributedTaskOrchestrationManager(discovery_manager)
    await orchestration_manager.start()
    
    print(f"\n✅ Test environment ready!")
    print(f"   - {len(agents)} mock agents running")
    print(f"   - Service discovery active")
    print(f"   - Task orchestration ready")
    
    return discovery_manager, agents, orchestration_manager


async def demo_basic_task_orchestration(orchestration_manager: DistributedTaskOrchestrationManager):
    """Basic Task Orchestration Demo"""
    print("\n" + "="*70)
    print("🎭 BASIC TASK ORCHESTRATION DEMO")
    print("="*70)
    
    # Single task submission
    print("\n📋 Submitting individual tasks...")
    
    tasks = [
        {
            'name': 'Calculate Statistics',
            'type': 'calculation',
            'capabilities': ['calculation', 'statistics'],
            'priority': TaskPriority.HIGH,
            'input_data': {'dataset': 'sales_data.csv', 'metrics': ['mean', 'std', 'variance']}
        },
        {
            'name': 'Process Data',
            'type': 'data_processing',
            'capabilities': ['data_processing'],
            'priority': TaskPriority.NORMAL,
            'input_data': {'source': 'database', 'filters': {'date': '2025-05-29'}}
        },
        {
            'name': 'Generate Report',
            'type': 'reporting',
            'capabilities': ['analytics', 'reporting'],
            'priority': TaskPriority.LOW,
            'input_data': {'template': 'monthly_report', 'format': 'pdf'}
        }
    ]
    
    submitted_task_ids = []
    
    for task_config in tasks:
        task_id = await orchestration_manager.submit_distributed_task(
            task_name=task_config['name'],
            task_type=task_config['type'],
            input_data=task_config['input_data'],
            required_capabilities=task_config['capabilities'],
            priority=task_config['priority'],
            timeout=60.0
        )
        
        submitted_task_ids.append(task_id)
        print(f"   ✅ Task submitted: {task_config['name']} ({task_id})")
        await asyncio.sleep(0.5)
    
    # Task durumlarını kontrol et
    print(f"\n📊 Checking task statuses...")
    await asyncio.sleep(3.0)  # Task'ların başlaması için bekle
    
    for task_id in submitted_task_ids:
        status = orchestration_manager.get_task_status(task_id)
        if status:
            print(f"   📋 Task {task_id}: {status['status']}")
    
    return submitted_task_ids


async def demo_consensus_based_tasks(orchestration_manager: DistributedTaskOrchestrationManager):
    """Consensus-based Task Demo"""
    print("\n" + "="*70)
    print("🤝 CONSENSUS-BASED TASK ORCHESTRATION DEMO")
    print("="*70)
    
    # Consensus gerektiren task'lar
    print("\n🗳️ Submitting tasks requiring consensus...")
    
    consensus_tasks = [
        {
            'name': 'Critical System Update',
            'type': 'system_update',
            'capabilities': ['system_admin'],
            'priority': TaskPriority.CRITICAL,
            'consensus_type': ConsensusType.UNANIMOUS,
            'input_data': {'update_package': 'security_patch_v2.1', 'restart_required': True}
        },
        {
            'name': 'Data Migration',
            'type': 'data_migration',
            'capabilities': ['data_processing', 'storage'],
            'priority': TaskPriority.HIGH,
            'consensus_type': ConsensusType.MAJORITY,
            'input_data': {'source_db': 'legacy_system', 'target_db': 'new_system'}
        }
    ]
    
    consensus_task_ids = []
    
    for task_config in consensus_tasks:
        try:
            task_id = await orchestration_manager.submit_distributed_task(
                task_name=task_config['name'],
                task_type=task_config['type'],
                input_data=task_config['input_data'],
                required_capabilities=task_config['capabilities'],
                priority=task_config['priority'],
                require_consensus=True,
                consensus_type=task_config['consensus_type']
            )
            
            consensus_task_ids.append(task_id)
            print(f"   ✅ Consensus task submitted: {task_config['name']} ({task_id})")
            
        except Exception as e:
            print(f"   ❌ Consensus task rejected: {task_config['name']} - {e}")
        
        await asyncio.sleep(2.0)  # Consensus için bekleme
    
    return consensus_task_ids


async def demo_task_dependencies(orchestration_manager: DistributedTaskOrchestrationManager):
    """Task Dependencies Demo"""
    print("\n" + "="*70)
    print("🔗 TASK DEPENDENCIES DEMO")
    print("="*70)
    
    print("\n🔗 Creating task chain with dependencies...")
    
    # İlk task - veri toplama
    task1_id = await orchestration_manager.submit_distributed_task(
        task_name="Data Collection",
        task_type="data_collection",
        input_data={'sources': ['api', 'database', 'files']},
        required_capabilities=['data_processing'],
        priority=TaskPriority.HIGH
    )
    print(f"   📋 Task 1 (Data Collection): {task1_id}")
    
    await asyncio.sleep(1.0)
    
    # İkinci task - veri işleme (task1'e bağımlı)
    task2_id = await orchestration_manager.submit_distributed_task(
        task_name="Data Processing",
        task_type="data_processing",
        input_data={'processing_type': 'cleaning_and_transformation'},
        required_capabilities=['data_processing', 'analytics'],
        priority=TaskPriority.NORMAL,
        dependencies=[task1_id]
    )
    print(f"   📋 Task 2 (Data Processing): {task2_id} (depends on {task1_id})")
    
    await asyncio.sleep(1.0)
    
    # Üçüncü task - ML model training (task2'ye bağımlı)
    task3_id = await orchestration_manager.submit_distributed_task(
        task_name="ML Model Training",
        task_type="machine_learning",
        input_data={'algorithm': 'random_forest', 'target': 'classification'},
        required_capabilities=['machine_learning'],
        priority=TaskPriority.NORMAL,
        dependencies=[task2_id]
    )
    print(f"   📋 Task 3 (ML Training): {task3_id} (depends on {task2_id})")
    
    await asyncio.sleep(1.0)
    
    # Dördüncü task - rapor oluşturma (task3'e bağımlı)
    task4_id = await orchestration_manager.submit_distributed_task(
        task_name="Report Generation",
        task_type="reporting",
        input_data={'report_type': 'ml_model_performance', 'format': 'dashboard'},
        required_capabilities=['analytics', 'reporting'],
        priority=TaskPriority.LOW,
        dependencies=[task3_id]
    )
    print(f"   📋 Task 4 (Report Generation): {task4_id} (depends on {task3_id})")
    
    # Dependency chain'i izle
    print(f"\n📊 Monitoring dependency chain execution...")
    dependency_tasks = [task1_id, task2_id, task3_id, task4_id]
    
    for i in range(10):  # 10 saniye izle
        await asyncio.sleep(1.0)
        
        statuses = []
        for task_id in dependency_tasks:
            status = orchestration_manager.get_task_status(task_id)
            if status:
                statuses.append(f"{task_id[:8]}:{status['status']}")
        
        print(f"   📊 Chain status: {' -> '.join(statuses)}")
    
    return dependency_tasks


async def demo_multi_agent_workflow(orchestration_manager: DistributedTaskOrchestrationManager):
    """Multi-Agent Workflow Demo"""
    print("\n" + "="*70)
    print("🔄 MULTI-AGENT WORKFLOW DEMO")
    print("="*70)
    
    print("\n🔄 Creating complex multi-agent workflow...")
    
    # Workflow task'ları tanımla
    workflow_tasks = [
        {
            'type': 'data_collection',
            'capabilities': ['data_processing'],
            'priority': TaskPriority.HIGH.value,
            'input_data': {'source': 'external_api', 'format': 'json'}
        },
        {
            'type': 'data_validation',
            'capabilities': ['data_processing', 'analytics'],
            'priority': TaskPriority.HIGH.value,
            'input_data': {'validation_rules': ['completeness', 'consistency']}
        },
        {
            'type': 'feature_engineering',
            'capabilities': ['machine_learning', 'analytics'],
            'priority': TaskPriority.NORMAL.value,
            'input_data': {'features': ['numerical', 'categorical', 'temporal']}
        },
        {
            'type': 'model_training',
            'capabilities': ['machine_learning'],
            'priority': TaskPriority.NORMAL.value,
            'input_data': {'algorithm': 'gradient_boosting', 'cv_folds': 5}
        },
        {
            'type': 'model_evaluation',
            'capabilities': ['machine_learning', 'analytics'],
            'priority': TaskPriority.NORMAL.value,
            'input_data': {'metrics': ['accuracy', 'precision', 'recall', 'f1']}
        },
        {
            'type': 'deployment',
            'capabilities': ['system_admin', 'communication'],
            'priority': TaskPriority.LOW.value,
            'input_data': {'environment': 'production', 'monitoring': True}
        }
    ]
    
    # Workflow'u başlat
    workflow_result = await orchestration_manager.coordinate_multi_agent_workflow(
        workflow_name="ML_Pipeline_Workflow",
        workflow_tasks=workflow_tasks,
        require_consensus=True
    )
    
    print(f"   🔄 Workflow result: {workflow_result['status']}")
    if workflow_result['status'] == 'started':
        print(f"   📋 Submitted {workflow_result['task_count']} tasks")
        print(f"   🆔 Workflow ID: {workflow_result['workflow_id']}")
        
        # Workflow progress'ini izle
        print(f"\n📊 Monitoring workflow progress...")
        for i in range(15):  # 15 saniye izle
            await asyncio.sleep(1.0)
            
            completed_count = 0
            for task_id in workflow_result['submitted_tasks']:
                status = orchestration_manager.get_task_status(task_id)
                if status and status['status'] == 'completed':
                    completed_count += 1
            
            progress = (completed_count / len(workflow_result['submitted_tasks'])) * 100
            print(f"   📊 Workflow progress: {progress:.1f}% ({completed_count}/{len(workflow_result['submitted_tasks'])} tasks completed)")
    
    return workflow_result


async def demo_distributed_decisions(orchestration_manager: DistributedTaskOrchestrationManager):
    """Distributed Decisions Demo"""
    print("\n" + "="*70)
    print("🤝 DISTRIBUTED DECISIONS DEMO")
    print("="*70)
    
    print("\n🗳️ Making distributed decisions...")
    
    # Çeşitli decision'lar
    decisions = [
        {
            'type': 'resource_allocation',
            'data': {'resource': 'gpu_cluster', 'allocation': '80%', 'duration': '2_hours'},
            'consensus_type': ConsensusType.MAJORITY
        },
        {
            'type': 'system_maintenance',
            'data': {'maintenance_type': 'security_update', 'downtime': '30_minutes'},
            'consensus_type': ConsensusType.WEIGHTED
        },
        {
            'type': 'emergency_response',
            'data': {'alert_level': 'high', 'response_team': 'security', 'action': 'isolate_system'},
            'consensus_type': ConsensusType.UNANIMOUS
        }
    ]
    
    decision_ids = []
    
    for decision in decisions:
        proposal_id = await orchestration_manager.make_distributed_decision(
            decision_type=decision['type'],
            decision_data=decision['data'],
            consensus_type=decision['consensus_type'],
            timeout=20.0
        )
        
        decision_ids.append(proposal_id)
        print(f"   🤝 Decision proposed: {decision['type']} ({proposal_id})")
        await asyncio.sleep(1.0)
    
    # Decision sonuçlarını bekle ve kontrol et
    print(f"\n📊 Waiting for decision results...")
    await asyncio.sleep(15.0)  # Decision'lar için bekleme
    
    for proposal_id in decision_ids:
        status = orchestration_manager.get_decision_status(proposal_id)
        if status:
            vote_summary = status.get('vote_summary', {})
            print(f"   🗳️ Decision {proposal_id[:8]}: {status['status']}")
            print(f"      Votes: {vote_summary.get('yes_votes', 0)} yes, {vote_summary.get('no_votes', 0)} no")
            print(f"      Success rate: {vote_summary.get('yes_percentage', 0):.1f}%")
    
    return decision_ids


async def demo_system_statistics(orchestration_manager: DistributedTaskOrchestrationManager):
    """System Statistics Demo"""
    print("\n" + "="*70)
    print("📊 SYSTEM STATISTICS DEMO")
    print("="*70)
    
    # Comprehensive stats
    stats = orchestration_manager.get_comprehensive_stats()
    
    print(f"\n🎭 Orchestration Manager Stats:")
    print(f"   Manager ID: {stats['manager_id']}")
    print(f"   Running: {stats['running']}")
    print(f"   Uptime: {stats['manager_stats']['uptime']:.1f}s")
    print(f"   Total Tasks Processed: {stats['manager_stats']['total_tasks_processed']}")
    print(f"   Total Decisions Made: {stats['manager_stats']['total_decisions_made']}")
    print(f"   Coordination Efficiency: {stats['manager_stats']['coordination_efficiency']:.1f}%")
    
    print(f"\n📋 Task Orchestrator Stats:")
    orch_stats = stats['orchestrator_stats']
    print(f"   Total Tasks Orchestrated: {orch_stats['stats']['total_tasks_orchestrated']}")
    
    scheduler_stats = orch_stats['scheduler_stats']
    print(f"   Pending Tasks: {scheduler_stats['pending_tasks']}")
    print(f"   Running Tasks: {scheduler_stats['running_tasks']}")
    print(f"   Completed Tasks: {scheduler_stats['completed_tasks']}")
    print(f"   Total Scheduled: {scheduler_stats['stats']['total_tasks_scheduled']}")
    print(f"   Total Completed: {scheduler_stats['stats']['total_tasks_completed']}")
    print(f"   Total Failed: {scheduler_stats['stats']['total_tasks_failed']}")
    
    print(f"\n🤝 Consensus Manager Stats:")
    consensus_stats = stats['consensus_stats']
    print(f"   Active Proposals: {consensus_stats['active_proposals']}")
    print(f"   Completed Proposals: {consensus_stats['completed_proposals']}")
    print(f"   Total Proposals: {consensus_stats['stats']['total_proposals']}")
    print(f"   Accepted Proposals: {consensus_stats['stats']['accepted_proposals']}")
    print(f"   Rejected Proposals: {consensus_stats['stats']['rejected_proposals']}")
    print(f"   Timeout Proposals: {consensus_stats['stats']['timeout_proposals']}")
    print(f"   Success Rate: {consensus_stats['stats']['consensus_success_rate']:.1f}%")
    print(f"   Average Decision Time: {consensus_stats['stats']['average_decision_time']:.2f}s")
    
    # Agent workloads
    print(f"\n🤖 Agent Workloads:")
    agent_performance = orch_stats.get('agent_performance', {})
    for agent_id, perf in agent_performance.items():
        if perf['total_tasks'] > 0:
            print(f"   {agent_id}:")
            print(f"     Total Tasks: {perf['total_tasks']}")
            print(f"     Completed: {perf['completed_tasks']}")
            print(f"     Failed: {perf['failed_tasks']}")
            print(f"     Success Rate: {perf['success_rate']:.1f}%")


async def cleanup_demo(discovery_manager: ServiceDiscoveryManager, 
                      agents: List[MockAgent], 
                      orchestration_manager: DistributedTaskOrchestrationManager):
    """Demo cleanup"""
    print("\n" + "="*70)
    print("🧹 CLEANUP")
    print("="*70)
    
    # Stop orchestration manager
    print("\n🛑 Stopping Orchestration Manager...")
    await orchestration_manager.stop()
    
    # Stop all agents
    print("\n🛑 Stopping all agents...")
    for agent in agents:
        if agent.running:
            await agent.stop(discovery_manager)
    
    # Stop discovery manager
    print("\n🛑 Stopping Service Discovery Manager...")
    await discovery_manager.stop()
    
    print("\n✅ Cleanup completed!")


async def main():
    """Ana demo fonksiyonu"""
    print("🎭 Distributed Task Orchestration Demo - Sprint 4.2")
    print("Orion Vision Core - Distributed Agent Coordination")
    print("="*70)
    
    try:
        # Test environment setup
        discovery_manager, agents, orchestration_manager = await setup_test_environment()
        
        await asyncio.sleep(2)
        
        # Basic Task Orchestration Demo
        await demo_basic_task_orchestration(orchestration_manager)
        
        await asyncio.sleep(3)
        
        # Consensus-based Tasks Demo
        await demo_consensus_based_tasks(orchestration_manager)
        
        await asyncio.sleep(3)
        
        # Task Dependencies Demo
        await demo_task_dependencies(orchestration_manager)
        
        await asyncio.sleep(3)
        
        # Multi-Agent Workflow Demo
        await demo_multi_agent_workflow(orchestration_manager)
        
        await asyncio.sleep(3)
        
        # Distributed Decisions Demo
        await demo_distributed_decisions(orchestration_manager)
        
        await asyncio.sleep(2)
        
        # System Statistics Demo
        await demo_system_statistics(orchestration_manager)
        
        # Cleanup
        await cleanup_demo(discovery_manager, agents, orchestration_manager)
        
        print("\n🎉 Task Orchestration Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
