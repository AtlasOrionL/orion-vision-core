#!/usr/bin/env python3
"""
Agent Learning System Tests - Sprint 3.3
Orion Vision Core - Machine Learning ve Adaptive Behavior Testleri

Bu script, agent_learning_system.py modülünün unit testlerini içerir.
"""

import unittest
import asyncio
import sys
import os
import time
import tempfile
import shutil
from unittest.mock import Mock, patch, AsyncMock

# Test modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))

from agent_learning_system import (
    LearningData, LearningType, AdaptationStrategy,
    KnowledgeBase, PatternRecognizer, MachineLearningEngine,
    ReinforcementLearningAgent, AgentLearningManager
)


class TestLearningData(unittest.TestCase):
    """LearningData class testleri"""

    def test_learning_data_creation(self):
        """LearningData oluşturma testi"""
        data = LearningData(
            agent_id="test_agent",
            learning_type=LearningType.SUPERVISED,
            input_data={"feature1": 1.0, "feature2": 2.0},
            output_data={"result": "success"},
            features=[1.0, 2.0, 3.0],
            reward=1.0
        )

        self.assertEqual(data.agent_id, "test_agent")
        self.assertEqual(data.learning_type, LearningType.SUPERVISED)
        self.assertEqual(data.input_data["feature1"], 1.0)
        self.assertEqual(data.output_data["result"], "success")
        self.assertEqual(data.features, [1.0, 2.0, 3.0])
        self.assertEqual(data.reward, 1.0)
        self.assertIsNotNone(data.data_id)
        self.assertIsNotNone(data.timestamp)

    def test_learning_data_to_dict(self):
        """LearningData to dict conversion testi"""
        data = LearningData(
            agent_id="test_agent",
            learning_type=LearningType.BEHAVIORAL,
            input_data={"test": "value"}
        )

        data_dict = data.to_dict()

        self.assertIn('data_id', data_dict)
        self.assertIn('agent_id', data_dict)
        self.assertIn('learning_type', data_dict)
        self.assertEqual(data_dict['agent_id'], "test_agent")
        self.assertEqual(data_dict['learning_type'], LearningType.BEHAVIORAL.value)

    def test_learning_data_from_dict(self):
        """LearningData from dict creation testi"""
        data_dict = {
            'data_id': 'test_id',
            'agent_id': 'test_agent',
            'learning_type': LearningType.REINFORCEMENT.value,
            'input_data': {'test': 'value'},
            'output_data': {'result': 'success'},
            'features': [1.0, 2.0],
            'reward': 0.8
        }

        data = LearningData.from_dict(data_dict)

        self.assertEqual(data.data_id, 'test_id')
        self.assertEqual(data.agent_id, 'test_agent')
        self.assertEqual(data.learning_type, LearningType.REINFORCEMENT)
        self.assertEqual(data.input_data['test'], 'value')
        self.assertEqual(data.reward, 0.8)


class TestKnowledgeBase(unittest.TestCase):
    """KnowledgeBase testleri"""

    def setUp(self):
        """Test setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.kb = KnowledgeBase("test_agent", self.temp_dir)

    def tearDown(self):
        """Test cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_knowledge_base_initialization(self):
        """Knowledge base başlatma testi"""
        self.assertEqual(self.kb.agent_id, "test_agent")
        self.assertEqual(self.kb.storage_path, self.temp_dir)
        self.assertIsInstance(self.kb.knowledge_cache, dict)
        self.assertTrue(os.path.exists(self.kb.db_path))

    def test_store_and_retrieve_knowledge(self):
        """Knowledge store ve retrieve testi"""
        # Store knowledge
        test_data = {"key1": "value1", "key2": 42}
        self.kb.store_knowledge("test_key", test_data, "test_category", 0.9)

        # Retrieve knowledge
        retrieved = self.kb.retrieve_knowledge("test_key")

        self.assertEqual(retrieved, test_data)

        # Test non-existent key
        non_existent = self.kb.retrieve_knowledge("non_existent")
        self.assertIsNone(non_existent)

    def test_store_and_get_patterns(self):
        """Pattern store ve get testi"""
        # Store patterns
        pattern_data = {"action": "start", "context": "morning"}
        self.kb.store_pattern("morning_routine", pattern_data)
        self.kb.store_pattern("morning_routine", pattern_data)  # Store again to increase frequency

        # Get patterns
        patterns = self.kb.get_patterns("morning_routine")

        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0]['pattern_name'], "morning_routine")
        self.assertEqual(patterns[0]['frequency'], 2)
        self.assertEqual(patterns[0]['pattern_data'], pattern_data)

    def test_store_and_get_learning_data(self):
        """Learning data store ve get testi"""
        # Create learning data
        learning_data = LearningData(
            agent_id="test_agent",
            learning_type=LearningType.SUPERVISED,
            input_data={"feature": 1.0},
            output_data={"result": "success"}
        )

        # Store learning data
        self.kb.store_learning_data(learning_data)

        # Get learning history
        history = self.kb.get_learning_history(LearningType.SUPERVISED, limit=10)

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].agent_id, "test_agent")
        self.assertEqual(history[0].learning_type, LearningType.SUPERVISED)

    def test_get_statistics(self):
        """Knowledge base istatistikleri testi"""
        # Add some test data
        self.kb.store_knowledge("key1", "value1", "category1")
        self.kb.store_knowledge("key2", "value2", "category2")
        self.kb.store_pattern("pattern1", {"data": "test"})

        learning_data = LearningData(agent_id="test_agent")
        self.kb.store_learning_data(learning_data)

        # Get statistics
        stats = self.kb.get_statistics()

        self.assertEqual(stats['agent_id'], "test_agent")
        self.assertEqual(stats['knowledge_count'], 2)
        self.assertEqual(stats['pattern_count'], 1)
        self.assertEqual(stats['learning_data_count'], 1)
        self.assertIn('cache_size', stats)


class TestPatternRecognizer(unittest.TestCase):
    """PatternRecognizer testleri"""

    def setUp(self):
        """Test setup"""
        self.pr = PatternRecognizer("test_agent")

    def test_pattern_recognizer_initialization(self):
        """Pattern recognizer başlatma testi"""
        self.assertEqual(self.pr.agent_id, "test_agent")
        self.assertIsInstance(self.pr.patterns, dict)
        self.assertEqual(self.pr.min_pattern_frequency, 3)

    def test_add_observation(self):
        """Observation ekleme testi"""
        observation = {
            "action": "start",
            "time_of_day": 8,
            "cpu_usage": 20.5
        }

        # Add observation
        self.pr.add_observation(observation)

        # Check if patterns were updated
        self.assertGreater(len(self.pr.patterns), 0)
        self.assertGreater(len(self.pr.sequence_patterns[self.pr.agent_id]), 0)
        self.assertGreater(len(self.pr.temporal_patterns[self.pr.agent_id]), 0)

    def test_frequent_patterns(self):
        """Frequent patterns testi"""
        # Add same observation multiple times
        observation = {"action": "process", "status": "running"}

        for _ in range(5):
            self.pr.add_observation(observation)

        # Get frequent patterns
        frequent_patterns = self.pr.get_frequent_patterns(min_frequency=3)

        self.assertGreater(len(frequent_patterns), 0)
        self.assertGreaterEqual(frequent_patterns[0]['frequency'], 3)

    def test_temporal_patterns(self):
        """Temporal patterns testi"""
        # Add observations with timestamps
        base_time = time.time()
        observations = [
            {"action": "start", "hour": 8},
            {"action": "process", "hour": 9},
            {"action": "stop", "hour": 17}
        ]

        for i, obs in enumerate(observations):
            timestamp = base_time + i * 3600  # 1 hour intervals
            self.pr.add_observation(obs, timestamp)

        # Get temporal patterns
        temporal_patterns = self.pr.get_temporal_patterns()

        self.assertIn('patterns', temporal_patterns)
        self.assertIn('statistics', temporal_patterns)
        self.assertEqual(temporal_patterns['statistics']['observation_count'], 3)

    def test_pattern_statistics(self):
        """Pattern istatistikleri testi"""
        # Add some observations
        for i in range(10):
            self.pr.add_observation({"action": f"action_{i % 3}", "value": i})

        # Get statistics
        stats = self.pr.get_pattern_statistics()

        self.assertEqual(stats['agent_id'], "test_agent")
        self.assertIn('total_patterns', stats)
        self.assertIn('frequent_patterns', stats)
        self.assertIn('max_frequency', stats)
        self.assertIn('average_frequency', stats)


class TestMachineLearningEngine(unittest.TestCase):
    """MachineLearningEngine testleri"""

    def setUp(self):
        """Test setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.ml_engine = MachineLearningEngine("test_agent", self.temp_dir)

    def tearDown(self):
        """Test cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ml_engine_initialization(self):
        """ML engine başlatma testi"""
        self.assertEqual(self.ml_engine.agent_id, "test_agent")
        self.assertEqual(self.ml_engine.storage_path, self.temp_dir)
        self.assertIsInstance(self.ml_engine.models, dict)

    def test_model_management(self):
        """Model yönetimi testi"""
        # Initially no models
        models = self.ml_engine.list_models()
        self.assertEqual(len(models), 0)

        # Test model info for non-existent model
        model_info = self.ml_engine.get_model_info("non_existent")
        self.assertIsNone(model_info)

        # Test model deletion for non-existent model
        delete_result = self.ml_engine.delete_model("non_existent")
        self.assertFalse(delete_result)

    @patch('agent_learning_system.ML_AVAILABLE', False)
    def test_ml_unavailable(self):
        """ML kütüphanesi mevcut değilken test"""
        # Create training data
        training_data = [
            LearningData(
                agent_id="test_agent",
                features=[1.0, 2.0],
                output_data={"success": True}
            )
        ]

        # Try to train classifier
        success = self.ml_engine.train_classifier(
            "test_model", training_data, "success"
        )

        self.assertFalse(success)

        # Try to train clusterer
        success = self.ml_engine.train_clusterer(
            "test_cluster", training_data, 2
        )

        self.assertFalse(success)

        # Try to predict
        prediction = self.ml_engine.predict("test_model", {"feature": 1.0})
        self.assertIsNone(prediction)


class TestReinforcementLearningAgent(unittest.TestCase):
    """ReinforcementLearningAgent testleri"""

    def setUp(self):
        """Test setup"""
        self.rl_agent = ReinforcementLearningAgent(
            agent_id="test_agent",
            learning_rate=0.1,
            discount_factor=0.9,
            exploration_rate=0.2
        )

    def test_rl_agent_initialization(self):
        """RL agent başlatma testi"""
        self.assertEqual(self.rl_agent.agent_id, "test_agent")
        self.assertEqual(self.rl_agent.learning_rate, 0.1)
        self.assertEqual(self.rl_agent.discount_factor, 0.9)
        self.assertEqual(self.rl_agent.exploration_rate, 0.2)
        self.assertIsInstance(self.rl_agent.q_table, dict)

    def test_get_action(self):
        """Action selection testi"""
        state = "test_state"
        actions = ["action1", "action2", "action3"]

        # Get action
        action = self.rl_agent.get_action(state, actions)

        self.assertIn(action, actions)

        # Check statistics update
        stats = self.rl_agent.get_learning_statistics()
        total_actions = stats['exploration_count'] + stats['exploitation_count']
        self.assertEqual(total_actions, 1)

    def test_update_q_value(self):
        """Q-value update testi"""
        state = "state1"
        action = "action1"
        reward = 1.0
        next_state = "state2"
        next_actions = ["action1", "action2"]

        # Initial Q-value should be 0
        initial_q = self.rl_agent.get_q_value(state, action)
        self.assertEqual(initial_q, 0.0)

        # Update Q-value
        self.rl_agent.update_q_value(state, action, reward, next_state, next_actions)

        # Q-value should be updated
        updated_q = self.rl_agent.get_q_value(state, action)
        self.assertNotEqual(updated_q, 0.0)

        # Check experience buffer
        self.assertEqual(len(self.rl_agent.experience_buffer), 1)

    def test_get_state_values(self):
        """State values testi"""
        state = "test_state"
        actions = ["action1", "action2"]

        # Update some Q-values
        self.rl_agent.update_q_value(state, "action1", 1.0, "next_state", actions)
        self.rl_agent.update_q_value(state, "action2", 0.5, "next_state", actions)

        # Get state values
        state_values = self.rl_agent.get_state_values(state)

        self.assertIn("action1", state_values)
        self.assertIn("action2", state_values)
        self.assertGreater(state_values["action1"], state_values["action2"])

    def test_decay_exploration(self):
        """Exploration decay testi"""
        initial_rate = self.rl_agent.exploration_rate

        # Decay exploration
        self.rl_agent.decay_exploration(decay_rate=0.9, min_rate=0.01)

        # Rate should be decreased
        self.assertLess(self.rl_agent.exploration_rate, initial_rate)

        # Test minimum rate
        for _ in range(100):  # Decay many times
            self.rl_agent.decay_exploration(decay_rate=0.9, min_rate=0.05)

        self.assertGreaterEqual(self.rl_agent.exploration_rate, 0.05)

    def test_learning_statistics(self):
        """Learning istatistikleri testi"""
        # Perform some learning
        self.rl_agent.update_q_value("state1", "action1", 1.0, "state2", ["action1"])
        self.rl_agent.update_q_value("state2", "action1", 0.5, "state1", ["action1"])

        # Get statistics
        stats = self.rl_agent.get_learning_statistics()

        self.assertEqual(stats['agent_id'], "test_agent")
        self.assertIn('q_table_size', stats)
        self.assertIn('experience_buffer_size', stats)
        self.assertIn('total_episodes', stats)
        self.assertIn('average_reward', stats)
        self.assertEqual(stats['total_episodes'], 2)


class TestAgentLearningManager(unittest.IsolatedAsyncioTestCase):
    """AgentLearningManager testleri"""

    async def asyncSetUp(self):
        """Async test setup"""
        self.temp_dir = tempfile.mkdtemp()
        config = {
            'learning_rate': 0.1,
            'discount_factor': 0.9,
            'exploration_rate': 0.1,
            'adaptation_strategy': 'gradual'
        }
        self.learning_manager = AgentLearningManager("test_agent", config)

        # Override storage paths to use temp directory
        self.learning_manager.knowledge_base.storage_path = self.temp_dir
        self.learning_manager.ml_engine.storage_path = self.temp_dir

    async def asyncTearDown(self):
        """Async test cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_learning_manager_initialization(self):
        """Learning manager başlatma testi"""
        self.assertEqual(self.learning_manager.agent_id, "test_agent")
        self.assertTrue(self.learning_manager.learning_enabled)
        self.assertEqual(self.learning_manager.adaptation_strategy, AdaptationStrategy.GRADUAL)

        # Check components
        self.assertIsNotNone(self.learning_manager.knowledge_base)
        self.assertIsNotNone(self.learning_manager.pattern_recognizer)
        self.assertIsNotNone(self.learning_manager.ml_engine)
        self.assertIsNotNone(self.learning_manager.rl_agent)

    async def test_learn_from_experience(self):
        """Experience'dan öğrenme testi"""
        experience = {
            'input': {'task_type': 'computation', 'complexity': 'high'},
            'output': {'success': True, 'duration': 2.5},
            'context': {'time_of_day': 10, 'system_load': 'medium'},
            'reward': 1.0,
            'state': 'processing',
            'action': 'optimize',
            'next_state': 'completed',
            'next_actions': ['report', 'cleanup'],
            'significant': True
        }

        # Learn from experience
        success = await self.learning_manager.learn_from_experience(experience)

        self.assertTrue(success)

    async def test_adapt_behavior(self):
        """Behavior adaptation testi"""
        # Test with good performance
        good_metrics = {
            'success_rate': 0.95,
            'avg_execution_time': 1.2,
            'error_rate': 0.02
        }

        result = await self.learning_manager.adapt_behavior(good_metrics)

        self.assertIn('adaptation_needed', result)
        self.assertIn('adaptations', result)
        self.assertIn('strategy', result)
        self.assertEqual(result['strategy'], 'gradual')

        # Test with poor performance
        poor_metrics = {
            'success_rate': 0.3,
            'avg_execution_time': 10.0,
            'error_rate': 0.4
        }

        result = await self.learning_manager.adapt_behavior(poor_metrics)

        self.assertIn('adaptation_needed', result)

    def test_get_recommendations(self):
        """Recommendation testi"""
        context = {
            'task_type': 'computation',
            'complexity': 'medium',
            'state': 'processing'
        }

        # Get recommendations
        recommendations = self.learning_manager.get_recommendations(context)

        self.assertIsInstance(recommendations, list)
        # Recommendations might be empty initially, which is fine

    def test_get_comprehensive_stats(self):
        """Comprehensive stats testi"""
        stats = self.learning_manager.get_comprehensive_stats()

        self.assertEqual(stats['agent_id'], "test_agent")
        self.assertIn('learning_enabled', stats)
        self.assertIn('adaptation_strategy', stats)
        self.assertIn('knowledge_base', stats)
        self.assertIn('pattern_recognizer', stats)
        self.assertIn('ml_engine', stats)
        self.assertIn('rl_agent', stats)

    async def test_learning_disabled(self):
        """Learning disabled durumu testi"""
        # Disable learning
        self.learning_manager.learning_enabled = False

        experience = {
            'input': {'test': 'data'},
            'output': {'result': 'success'},
            'reward': 1.0
        }

        # Try to learn
        success = await self.learning_manager.learn_from_experience(experience)

        self.assertFalse(success)


def run_learning_system_tests():
    """Learning system testlerini çalıştır"""
    print("🧠 Agent Learning System Tests - Sprint 3.3")
    print("=" * 70)

    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestLearningData))
    suite.addTests(loader.loadTestsFromTestCase(TestKnowledgeBase))
    suite.addTests(loader.loadTestsFromTestCase(TestPatternRecognizer))
    suite.addTests(loader.loadTestsFromTestCase(TestMachineLearningEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestReinforcementLearningAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentLearningManager))

    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)

    # Testleri çalıştır
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 Tüm Agent Learning System testleri başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız oldu!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_learning_system_tests()
    sys.exit(0 if success else 1)
