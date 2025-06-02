#!/usr/bin/env python3
"""
Task Orchestration Tests - Sprint 4.2
Orion Vision Core - Distributed Agent Coordination

Bu modül, Task Orchestration sisteminin tüm bileşenlerini test eder.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import unittest
import asyncio
import time
import tempfile
import shutil
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# Test edilecek modülleri import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from jobone.vision_core.task_orchestration import (
    TaskDefinition,
    TaskExecution,
    TaskStatus,
    TaskPriority,
    TaskScheduler,
    TaskOrchestrator,
    ConsensusProposal,
    ConsensusType,
    ConsensusManager,
    DistributedTaskOrchestrationManager
)


class TestTaskDefinition(unittest.TestCase):
    """TaskDefinition testleri"""

    def setUp(self):
        """Test setup"""
        self.task_def = TaskDefinition(
            task_name="test_task",
            task_type="calculation",
            required_capabilities=["math", "statistics"],
            priority=TaskPriority.HIGH,
            timeout=120.0
        )

    def test_task_definition_creation(self):
        """TaskDefinition oluşturma testi"""
        self.assertEqual(self.task_def.task_name, "test_task")
        self.assertEqual(self.task_def.task_type, "calculation")
        self.assertEqual(self.task_def.required_capabilities, ["math", "statistics"])
        self.assertEqual(self.task_def.priority, TaskPriority.HIGH)
        self.assertEqual(self.task_def.timeout, 120.0)
        self.assertIsNotNone(self.task_def.task_id)

    def test_task_definition_to_dict(self):
        """TaskDefinition to dict conversion testi"""
        data = self.task_def.to_dict()

        self.assertIn('task_id', data)
        self.assertEqual(data['task_name'], "test_task")
        self.assertEqual(data['task_type'], "calculation")
        self.assertEqual(data['required_capabilities'], ["math", "statistics"])
        self.assertEqual(data['priority'], TaskPriority.HIGH.value)
        self.assertEqual(data['timeout'], 120.0)

    def test_task_definition_from_dict(self):
        """TaskDefinition from dict creation testi"""
        data = {
            'task_name': 'test_task_2',
            'task_type': 'data_processing',
            'required_capabilities': ['data'],
            'priority': TaskPriority.NORMAL.value,
            'timeout': 300.0
        }

        task_def = TaskDefinition.from_dict(data)

        self.assertEqual(task_def.task_name, "test_task_2")
        self.assertEqual(task_def.task_type, "data_processing")
        self.assertEqual(task_def.required_capabilities, ["data"])
        self.assertEqual(task_def.priority, TaskPriority.NORMAL)
        self.assertEqual(task_def.timeout, 300.0)


class TestTaskExecution(unittest.TestCase):
    """TaskExecution testleri"""

    def setUp(self):
        """Test setup"""
        self.execution = TaskExecution(task_id="test_task_123")

    def test_task_execution_creation(self):
        """TaskExecution oluşturma testi"""
        self.assertEqual(self.execution.task_id, "test_task_123")
        self.assertEqual(self.execution.status, TaskStatus.PENDING)
        self.assertEqual(self.execution.progress_percentage, 0.0)
        self.assertEqual(self.execution.attempt_number, 1)

    def test_start_execution(self):
        """Task execution başlatma testi"""
        self.execution.start_execution("agent_001", "service_123")

        self.assertEqual(self.execution.assigned_agent, "agent_001")
        self.assertEqual(self.execution.assigned_service_id, "service_123")
        self.assertEqual(self.execution.status, TaskStatus.RUNNING)
        self.assertIsNotNone(self.execution.start_time)
        self.assertEqual(self.execution.progress_percentage, 0.0)

    def test_complete_execution(self):
        """Task execution tamamlama testi"""
        self.execution.start_execution("agent_001", "service_123")

        output_data = {"result": "success", "value": 42}
        self.execution.complete_execution(output_data)

        self.assertEqual(self.execution.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(self.execution.end_time)
        self.assertIsNotNone(self.execution.duration)
        self.assertEqual(self.execution.progress_percentage, 100.0)
        self.assertEqual(self.execution.output_data, output_data)

    def test_fail_execution(self):
        """Task execution başarısızlık testi"""
        self.execution.start_execution("agent_001", "service_123")

        error_message = "Calculation failed"
        error_details = {"error_code": "CALC_001"}
        self.execution.fail_execution(error_message, error_details)

        self.assertEqual(self.execution.status, TaskStatus.FAILED)
        self.assertIsNotNone(self.execution.end_time)
        self.assertEqual(self.execution.error_message, error_message)
        self.assertEqual(self.execution.error_details, error_details)

    def test_update_progress(self):
        """Progress güncelleme testi"""
        self.execution.update_progress(50.0, "Half completed")

        self.assertEqual(self.execution.progress_percentage, 50.0)
        self.assertEqual(self.execution.progress_message, "Half completed")
        self.assertEqual(len(self.execution.checkpoints), 1)

        checkpoint = self.execution.checkpoints[0]
        self.assertEqual(checkpoint['percentage'], 50.0)
        self.assertEqual(checkpoint['message'], "Half completed")

    def test_add_retry_attempt(self):
        """Retry attempt ekleme testi"""
        self.execution.start_execution("agent_001", "service_123")
        self.execution.fail_execution("First attempt failed")

        self.execution.add_retry_attempt("First attempt failed")

        self.assertEqual(self.execution.attempt_number, 2)
        self.assertEqual(self.execution.status, TaskStatus.PENDING)
        self.assertEqual(len(self.execution.retry_history), 1)

        retry_record = self.execution.retry_history[0]
        self.assertEqual(retry_record['attempt'], 1)
        self.assertEqual(retry_record['error'], "First attempt failed")


class TestTaskScheduler(unittest.IsolatedAsyncioTestCase):
    """TaskScheduler testleri"""

    async def asyncSetUp(self):
        """Async test setup"""
        self.scheduler = TaskScheduler()

    async def asyncTearDown(self):
        """Async test cleanup"""
        await self.scheduler.stop()

    def test_scheduler_initialization(self):
        """Scheduler başlatma testi"""
        self.assertFalse(self.scheduler.running)
        self.assertEqual(len(self.scheduler.pending_tasks), 0)
        self.assertEqual(len(self.scheduler.running_tasks), 0)
        self.assertEqual(len(self.scheduler.completed_tasks), 0)

    async def test_scheduler_start_stop(self):
        """Scheduler start/stop testi"""
        await self.scheduler.start()
        self.assertTrue(self.scheduler.running)

        await self.scheduler.stop()
        self.assertFalse(self.scheduler.running)

    def test_submit_task(self):
        """Task gönderme testi"""
        task_def = TaskDefinition(
            task_name="test_task",
            task_type="calculation",
            priority=TaskPriority.HIGH
        )

        success = self.scheduler.submit_task(task_def)

        self.assertTrue(success)
        self.assertIn(task_def.task_id, self.scheduler.pending_tasks)
        self.assertEqual(len(self.scheduler.task_queues[TaskPriority.HIGH]), 1)
        self.assertEqual(self.scheduler.scheduler_stats['total_tasks_scheduled'], 1)

    def test_get_next_task(self):
        """Sonraki task alma testi"""
        # Farklı priority'lerde task'lar ekle
        high_task = TaskDefinition(task_name="high_task", priority=TaskPriority.HIGH)
        normal_task = TaskDefinition(task_name="normal_task", priority=TaskPriority.NORMAL)
        low_task = TaskDefinition(task_name="low_task", priority=TaskPriority.LOW)

        self.scheduler.submit_task(normal_task)
        self.scheduler.submit_task(low_task)
        self.scheduler.submit_task(high_task)

        # En yüksek priority'li task'ı almalı
        next_task = self.scheduler.get_next_task()
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.task_name, "high_task")
        self.assertNotIn(high_task.task_id, self.scheduler.pending_tasks)

    def test_cancel_task(self):
        """Task iptal etme testi"""
        task_def = TaskDefinition(task_name="test_task")
        self.scheduler.submit_task(task_def)

        success = self.scheduler.cancel_task(task_def.task_id)

        self.assertTrue(success)
        self.assertNotIn(task_def.task_id, self.scheduler.pending_tasks)

    def test_task_execution_lifecycle(self):
        """Task execution lifecycle testi"""
        task_def = TaskDefinition(task_name="test_task")

        # Start execution
        execution = self.scheduler.start_task_execution(task_def, "agent_001", "service_123")

        self.assertIn(task_def.task_id, self.scheduler.running_tasks)
        self.assertEqual(execution.assigned_agent, "agent_001")
        self.assertEqual(execution.status, TaskStatus.RUNNING)

        # Complete execution
        output_data = {"result": "success"}
        success = self.scheduler.complete_task_execution(task_def.task_id, output_data)

        self.assertTrue(success)
        self.assertNotIn(task_def.task_id, self.scheduler.running_tasks)
        self.assertIn(task_def.task_id, self.scheduler.completed_tasks)

        completed_execution = self.scheduler.completed_tasks[task_def.task_id]
        self.assertEqual(completed_execution.status, TaskStatus.COMPLETED)
        self.assertEqual(completed_execution.output_data, output_data)


class TestConsensusProposal(unittest.TestCase):
    """ConsensusProposal testleri"""

    def setUp(self):
        """Test setup"""
        self.proposal = ConsensusProposal(
            proposer_id="agent_001",
            proposal_type="resource_allocation",
            proposal_data={"resource": "cpu", "amount": "50%"},
            consensus_type=ConsensusType.MAJORITY
        )

    def test_proposal_creation(self):
        """Proposal oluşturma testi"""
        self.assertEqual(self.proposal.proposer_id, "agent_001")
        self.assertEqual(self.proposal.proposal_type, "resource_allocation")
        self.assertEqual(self.proposal.consensus_type, ConsensusType.MAJORITY)
        self.assertEqual(self.proposal.status, "pending")
        self.assertIsNotNone(self.proposal.proposal_id)

    def test_add_vote(self):
        """Vote ekleme testi"""
        self.proposal.add_vote("agent_001", True, 1.0)
        self.proposal.add_vote("agent_002", False, 1.5)

        self.assertEqual(len(self.proposal.votes), 2)
        self.assertTrue(self.proposal.votes["agent_001"])
        self.assertFalse(self.proposal.votes["agent_002"])
        self.assertEqual(self.proposal.vote_weights["agent_002"], 1.5)

    def test_vote_summary(self):
        """Vote özeti testi"""
        self.proposal.add_vote("agent_001", True, 1.0)
        self.proposal.add_vote("agent_002", True, 2.0)
        self.proposal.add_vote("agent_003", False, 1.0)

        summary = self.proposal.get_vote_summary()

        self.assertEqual(summary['total_votes'], 3)
        self.assertEqual(summary['yes_votes'], 2)
        self.assertEqual(summary['no_votes'], 1)
        self.assertEqual(summary['total_weight'], 4.0)
        self.assertEqual(summary['yes_weight'], 3.0)
        self.assertEqual(summary['no_weight'], 1.0)

    def test_check_consensus_majority(self):
        """Majority consensus kontrolü testi"""
        # Majority yok
        self.proposal.add_vote("agent_001", True)
        self.proposal.add_vote("agent_002", False)
        self.assertFalse(self.proposal.check_consensus())

        # Majority var
        self.proposal.add_vote("agent_003", True)
        self.assertTrue(self.proposal.check_consensus())

    def test_check_consensus_unanimous(self):
        """Unanimous consensus kontrolü testi"""
        self.proposal.consensus_type = ConsensusType.UNANIMOUS

        # Unanimous değil
        self.proposal.add_vote("agent_001", True)
        self.proposal.add_vote("agent_002", False)
        self.assertFalse(self.proposal.check_consensus())

        # Unanimous
        self.proposal.votes["agent_002"] = True
        self.assertTrue(self.proposal.check_consensus())


class TestConsensusManager(unittest.IsolatedAsyncioTestCase):
    """ConsensusManager testleri"""

    async def asyncSetUp(self):
        """Async test setup"""
        self.consensus_manager = ConsensusManager()

    async def asyncTearDown(self):
        """Async test cleanup"""
        await self.consensus_manager.stop()

    def test_consensus_manager_initialization(self):
        """Consensus manager başlatma testi"""
        self.assertFalse(self.consensus_manager.running)
        self.assertEqual(len(self.consensus_manager.active_proposals), 0)
        self.assertEqual(len(self.consensus_manager.completed_proposals), 0)

    async def test_consensus_manager_start_stop(self):
        """Consensus manager start/stop testi"""
        await self.consensus_manager.start()
        self.assertTrue(self.consensus_manager.running)

        await self.consensus_manager.stop()
        self.assertFalse(self.consensus_manager.running)

    async def test_propose_decision(self):
        """Decision proposal testi"""
        proposal_id = await self.consensus_manager.propose_decision(
            proposer_id="agent_001",
            proposal_type="resource_allocation",
            proposal_data={"resource": "memory", "amount": "2GB"},
            consensus_type=ConsensusType.MAJORITY,
            timeout=10.0
        )

        self.assertIsNotNone(proposal_id)
        self.assertIn(proposal_id, self.consensus_manager.active_proposals)
        self.assertEqual(self.consensus_manager.consensus_stats['total_proposals'], 1)

    async def test_cast_vote(self):
        """Vote verme testi"""
        proposal_id = await self.consensus_manager.propose_decision(
            proposer_id="agent_001",
            proposal_type="test_decision",
            proposal_data={"test": "data"}
        )

        success = await self.consensus_manager.cast_vote(proposal_id, "agent_002", True, 1.0)

        self.assertTrue(success)

        # Proposal completed proposals'a taşınmış olabilir (consensus sağlandıysa)
        if proposal_id in self.consensus_manager.active_proposals:
            proposal = self.consensus_manager.active_proposals[proposal_id]
        else:
            proposal = self.consensus_manager.completed_proposals[proposal_id]

        self.assertIn("agent_002", proposal.votes)
        self.assertTrue(proposal.votes["agent_002"])

    def test_get_proposal_status(self):
        """Proposal status alma testi"""
        # Non-existent proposal
        status = self.consensus_manager.get_proposal_status("non_existent")
        self.assertIsNone(status)


class TestDistributedTaskOrchestrationManager(unittest.IsolatedAsyncioTestCase):
    """DistributedTaskOrchestrationManager testleri"""

    async def asyncSetUp(self):
        """Async test setup"""
        self.orchestration_manager = DistributedTaskOrchestrationManager()

    async def asyncTearDown(self):
        """Async test cleanup"""
        await self.orchestration_manager.stop()

    def test_orchestration_manager_initialization(self):
        """Orchestration manager başlatma testi"""
        self.assertFalse(self.orchestration_manager.running)
        self.assertIsNotNone(self.orchestration_manager.task_orchestrator)
        self.assertIsNotNone(self.orchestration_manager.consensus_manager)
        self.assertIsNotNone(self.orchestration_manager.manager_id)

    async def test_orchestration_manager_start_stop(self):
        """Orchestration manager start/stop testi"""
        await self.orchestration_manager.start()
        self.assertTrue(self.orchestration_manager.running)

        await self.orchestration_manager.stop()
        self.assertFalse(self.orchestration_manager.running)

    async def test_submit_distributed_task(self):
        """Distributed task gönderme testi"""
        await self.orchestration_manager.start()

        task_id = await self.orchestration_manager.submit_distributed_task(
            task_name="test_task",
            task_type="calculation",
            input_data={"x": 10, "y": 20},
            required_capabilities=["math"],
            priority=TaskPriority.NORMAL,
            require_consensus=False
        )

        self.assertIsNotNone(task_id)
        self.assertEqual(self.orchestration_manager.manager_stats['total_tasks_processed'], 1)

        # Task status kontrolü
        status = self.orchestration_manager.get_task_status(task_id)
        self.assertIsNotNone(status)

    def test_get_comprehensive_stats(self):
        """Comprehensive stats testi"""
        stats = self.orchestration_manager.get_comprehensive_stats()

        self.assertIn('manager_id', stats)
        self.assertIn('running', stats)
        self.assertIn('manager_stats', stats)
        self.assertIn('orchestrator_stats', stats)
        self.assertIn('consensus_stats', stats)


def run_task_orchestration_tests():
    """Task Orchestration testlerini çalıştır"""
    print("🎭 Task Orchestration Tests - Sprint 4.2")
    print("=" * 70)

    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestTaskDefinition))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskScheduler))
    suite.addTests(loader.loadTestsFromTestCase(TestConsensusProposal))
    suite.addTests(loader.loadTestsFromTestCase(TestConsensusManager))
    suite.addTests(loader.loadTestsFromTestCase(TestDistributedTaskOrchestrationManager))

    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)

    # Testleri çalıştır
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 Tüm Task Orchestration testleri başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız oldu!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_task_orchestration_tests()
    sys.exit(0 if success else 1)
