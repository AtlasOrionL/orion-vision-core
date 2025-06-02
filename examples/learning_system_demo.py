#!/usr/bin/env python3
"""
Learning System Demo - Sprint 3.3
Orion Vision Core - Machine Learning ve Adaptive Behavior Demonstrasyonu

Bu script, agent learning system'in yeteneklerini gösterir:
- Knowledge Base ve Pattern Recognition
- Machine Learning (Supervised/Unsupervised)
- Reinforcement Learning
- Adaptive Behavior ve Recommendations

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import sys
import os
import time
import asyncio
import signal
import json
import random
import numpy as np
from pathlib import Path

# Learning system modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from agent_learning_system import (
    AgentLearningManager, KnowledgeBase, PatternRecognizer,
    MachineLearningEngine, ReinforcementLearningAgent,
    LearningData, LearningType, AdaptationStrategy
)
from dynamic_agent_loader import DynamicAgentLoader, get_global_loader


class LearningSystemDemo:
    """
    Learning System Demo

    Bu sınıf, agent learning system'in tüm özelliklerini
    göstermek için tasarlanmıştır.
    """

    def __init__(self):
        """Demo başlatıcı"""
        self.running = True
        self.demo_agent_id = "demo_learning_agent"
        self.learning_manager = None
        self.test_agents = []

        # Demo data
        self.demo_experiences = []
        self.demo_patterns = []
        self.demo_models = []

        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print("🧠 Learning System Demo - Sprint 3.3")
        print("=" * 70)

    def _signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown"""
        print(f"\n🛑 Signal {signum} received, shutting down...")
        self.running = False
        asyncio.create_task(self._cleanup_all())
        sys.exit(0)

    async def run_demo(self):
        """Ana demo fonksiyonu"""
        try:
            # 1. Knowledge Base demonstrasyonu
            await self._demo_knowledge_base()

            # 2. Pattern Recognition demonstrasyonu
            await self._demo_pattern_recognition()

            # 3. Machine Learning demonstrasyonu
            await self._demo_machine_learning()

            # 4. Reinforcement Learning demonstrasyonu
            await self._demo_reinforcement_learning()

            # 5. Agent Learning Manager demonstrasyonu
            await self._demo_learning_manager()

            # 6. Dynamic Learning Agent demonstrasyonu
            await self._demo_dynamic_learning_agent()

            # 7. Adaptive Behavior demonstrasyonu
            await self._demo_adaptive_behavior()

            print("\n🎉 Learning System Demo completed successfully!")

        except KeyboardInterrupt:
            print("\n⚠️ Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
        finally:
            await self._cleanup_all()

    async def _demo_knowledge_base(self):
        """Knowledge Base demonstrasyonu"""
        print("\n📋 1. Knowledge Base - Persistent Learning Storage")
        print("-" * 50)

        # Knowledge base oluştur
        kb = KnowledgeBase(self.demo_agent_id)

        # Test knowledge'ları ekle
        test_knowledge = [
            ("user_preferences", {"theme": "dark", "language": "en"}, "user_data"),
            ("system_performance", {"cpu_usage": 45.2, "memory_usage": 67.8}, "metrics"),
            ("learned_patterns", {"frequent_actions": ["start", "process", "stop"]}, "patterns"),
            ("model_parameters", {"learning_rate": 0.1, "epochs": 100}, "ml_config"),
            ("communication_stats", {"messages_sent": 150, "success_rate": 0.95}, "communication")
        ]

        print("💾 Storing knowledge...")
        for key, value, category in test_knowledge:
            confidence = random.uniform(0.7, 1.0)
            kb.store_knowledge(key, value, category, confidence)
            print(f"   ✅ Stored: {key} ({category}) - confidence: {confidence:.2f}")

        # Knowledge'ları geri oku
        print("\n📖 Retrieving knowledge...")
        for key, _, _ in test_knowledge:
            retrieved = kb.retrieve_knowledge(key)
            if retrieved:
                print(f"   📚 Retrieved: {key} = {retrieved}")

        # Pattern'ları ekle
        print("\n🔍 Storing patterns...")
        test_patterns = [
            ("morning_routine", {"time": "08:00", "actions": ["start", "check_status"]}),
            ("error_handling", {"trigger": "exception", "response": "retry_with_backoff"}),
            ("user_interaction", {"input": "request", "output": "response", "satisfaction": 0.9})
        ]

        for pattern_name, pattern_data in test_patterns:
            kb.store_pattern(pattern_name, pattern_data)
            print(f"   🔍 Stored pattern: {pattern_name}")

        # Pattern'ları getir
        patterns = kb.get_patterns(limit=5)
        print(f"\n📊 Retrieved {len(patterns)} patterns:")
        for pattern in patterns:
            print(f"   Pattern: {pattern['pattern_name']} (frequency: {pattern['frequency']})")

        # Learning data ekle
        print("\n🧠 Storing learning data...")
        for i in range(5):
            learning_data = LearningData(
                agent_id=self.demo_agent_id,
                learning_type=LearningType.BEHAVIORAL,
                input_data={"action": f"action_{i}", "context": f"context_{i}"},
                output_data={"result": "success" if i % 2 == 0 else "failure"},
                performance_metrics={"accuracy": random.uniform(0.7, 0.95)},
                features=[random.uniform(0, 1) for _ in range(5)]
            )
            kb.store_learning_data(learning_data)
            print(f"   🧠 Stored learning data {i+1}")

        # İstatistikleri göster
        stats = kb.get_statistics()
        print(f"\n📊 Knowledge Base Statistics:")
        print(f"   Knowledge entries: {stats['knowledge_count']}")
        print(f"   Patterns: {stats['pattern_count']}")
        print(f"   Learning data: {stats['learning_data_count']}")
        print(f"   Cache size: {stats['cache_size']}")

    async def _demo_pattern_recognition(self):
        """Pattern Recognition demonstrasyonu"""
        print("\n📋 2. Pattern Recognition - Behavioral Pattern Detection")
        print("-" * 50)

        # Pattern recognizer oluştur
        pr = PatternRecognizer(self.demo_agent_id)

        # Test observations ekle
        print("👁️ Adding observations...")
        test_observations = [
            {"action": "start", "time_of_day": 8, "user_present": True, "cpu_usage": 20},
            {"action": "process", "time_of_day": 9, "user_present": True, "cpu_usage": 60},
            {"action": "process", "time_of_day": 10, "user_present": True, "cpu_usage": 55},
            {"action": "stop", "time_of_day": 17, "user_present": False, "cpu_usage": 15},
            {"action": "start", "time_of_day": 8, "user_present": True, "cpu_usage": 25},
            {"action": "process", "time_of_day": 9, "user_present": True, "cpu_usage": 65},
            {"action": "error", "time_of_day": 14, "user_present": True, "cpu_usage": 90},
            {"action": "restart", "time_of_day": 14, "user_present": True, "cpu_usage": 30}
        ]

        for i, obs in enumerate(test_observations):
            timestamp = time.time() + i * 3600  # 1 hour intervals
            pr.add_observation(obs, timestamp)
            print(f"   👁️ Added observation {i+1}: {obs['action']} at hour {obs['time_of_day']}")

        # Frequent patterns getir
        print("\n🔍 Analyzing frequent patterns...")
        frequent_patterns = pr.get_frequent_patterns(min_frequency=2)
        print(f"Found {len(frequent_patterns)} frequent patterns:")
        for pattern in frequent_patterns:
            print(f"   🔍 Pattern: {pattern['signature'][:50]}... (freq: {pattern['frequency']})")

        # Temporal patterns analiz et
        print("\n⏰ Analyzing temporal patterns...")
        temporal_patterns = pr.get_temporal_patterns()
        print(f"Temporal analysis results:")
        print(f"   Observations: {temporal_patterns['statistics']['observation_count']}")
        print(f"   Time span: {temporal_patterns['statistics']['time_span']:.1f} seconds")
        print(f"   Average interval: {temporal_patterns['statistics']['average_interval']:.1f} seconds")

        if temporal_patterns['patterns']:
            print(f"   Detected {len(temporal_patterns['patterns'])} temporal patterns:")
            for pattern in temporal_patterns['patterns']:
                print(f"     ⏰ {pattern['pattern']}")

        # Pattern statistics
        stats = pr.get_pattern_statistics()
        print(f"\n📊 Pattern Recognition Statistics:")
        print(f"   Total patterns: {stats['total_patterns']}")
        print(f"   Frequent patterns: {stats['frequent_patterns']}")
        print(f"   Max frequency: {stats['max_frequency']}")
        print(f"   Average frequency: {stats['average_frequency']:.2f}")

    async def _demo_machine_learning(self):
        """Machine Learning demonstrasyonu"""
        print("\n📋 3. Machine Learning - Supervised & Unsupervised Learning")
        print("-" * 50)

        # ML engine oluştur
        ml_engine = MachineLearningEngine(self.demo_agent_id)

        # Training data oluştur
        print("🔬 Creating training data...")
        training_data = []

        # Simulated task execution data
        for i in range(50):
            success = random.choice([True, False])
            execution_time = random.uniform(0.5, 5.0)
            cpu_usage = random.uniform(20, 80)
            memory_usage = random.uniform(30, 90)

            learning_data = LearningData(
                agent_id=self.demo_agent_id,
                learning_type=LearningType.SUPERVISED,
                input_data={
                    "execution_time": execution_time,
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage
                },
                output_data={"success": success},
                features=[execution_time, cpu_usage, memory_usage, i % 24],  # hour of day
                performance_metrics={"accuracy": 1.0 if success else 0.0}
            )
            training_data.append(learning_data)

        print(f"   ✅ Created {len(training_data)} training samples")

        # Classifier eğit
        print("\n🤖 Training classifier...")
        classifier_success = ml_engine.train_classifier(
            model_name="task_success_predictor",
            training_data=training_data,
            target_feature="success"
        )

        if classifier_success:
            print("   ✅ Classifier training successful!")

            # Test prediction
            test_input = {
                "execution_time": 2.5,
                "cpu_usage": 45.0,
                "memory_usage": 60.0,
                "hour": 10
            }

            prediction = ml_engine.predict("task_success_predictor", test_input)
            if prediction:
                print(f"   🔮 Prediction for test input: {prediction['prediction']}")
                print(f"   🎯 Confidence: {prediction['confidence']:.3f}")

        # Clustering eğit
        print("\n🔍 Training clusterer...")
        clustering_success = ml_engine.train_clusterer(
            model_name="behavior_clusters",
            training_data=training_data,
            n_clusters=3
        )

        if clustering_success:
            print("   ✅ Clustering training successful!")

        # Model bilgilerini göster
        models = ml_engine.list_models()
        print(f"\n📊 Trained Models ({len(models)}):")
        for model in models:
            print(f"   🤖 {model['model_name']} ({model['learning_type']})")
            print(f"      Parameters: {model['parameters']}")
            if model['performance_history']:
                latest_perf = model['performance_history'][-1]
                print(f"      Latest performance: {latest_perf}")

    async def _demo_reinforcement_learning(self):
        """Reinforcement Learning demonstrasyonu"""
        print("\n📋 4. Reinforcement Learning - Q-Learning Agent")
        print("-" * 50)

        # RL agent oluştur
        rl_agent = ReinforcementLearningAgent(
            agent_id=self.demo_agent_id,
            learning_rate=0.1,
            discount_factor=0.9,
            exploration_rate=0.2
        )

        # Simulated environment
        states = ["idle", "processing", "waiting", "error"]
        actions = ["start", "process", "wait", "restart", "stop"]

        print("🎮 Running RL simulation...")

        # Training episodes
        for episode in range(20):
            current_state = random.choice(states)

            for step in range(5):
                # Get action from RL agent
                action = rl_agent.get_action(current_state, actions)

                # Simulate environment response
                next_state = random.choice(states)

                # Calculate reward based on action-state combination
                reward = 0.0
                if current_state == "error" and action == "restart":
                    reward = 1.0  # Good action
                elif current_state == "idle" and action == "start":
                    reward = 0.8  # Good action
                elif current_state == "processing" and action == "stop":
                    reward = -0.5  # Bad action
                else:
                    reward = random.uniform(-0.2, 0.2)  # Neutral

                # Update Q-value
                rl_agent.update_q_value(
                    state=current_state,
                    action=action,
                    reward=reward,
                    next_state=next_state,
                    next_actions=actions
                )

                current_state = next_state

            if episode % 5 == 0:
                print(f"   🎮 Episode {episode+1}/20 completed")

        # Show learned Q-values
        print("\n🧠 Learned Q-values (sample):")
        for state in states[:2]:  # Show first 2 states
            state_values = rl_agent.get_state_values(state)
            if state_values:
                best_action = max(state_values, key=state_values.get)
                print(f"   State '{state}': Best action = '{best_action}' (Q={state_values[best_action]:.3f})")

        # RL statistics
        rl_stats = rl_agent.get_learning_statistics()
        print(f"\n📊 RL Agent Statistics:")
        print(f"   Q-table size: {rl_stats['q_table_size']}")
        print(f"   Experience buffer: {rl_stats['experience_buffer_size']}")
        print(f"   Total episodes: {rl_stats['total_episodes']}")
        print(f"   Average reward: {rl_stats['average_reward']:.3f}")
        print(f"   Exploration rate: {rl_stats['exploration_rate']:.3f}")
        print(f"   Exploration count: {rl_stats['exploration_count']}")
        print(f"   Exploitation count: {rl_stats['exploitation_count']}")

    async def _demo_learning_manager(self):
        """Agent Learning Manager demonstrasyonu"""
        print("\n📋 5. Agent Learning Manager - Integrated Learning System")
        print("-" * 50)

        # Learning manager oluştur
        config = {
            'learning_rate': 0.15,
            'discount_factor': 0.9,
            'exploration_rate': 0.1,
            'adaptation_strategy': 'gradual'
        }

        self.learning_manager = AgentLearningManager(self.demo_agent_id, config)

        print("🧠 Learning Manager initialized with integrated components")

        # Simulated experiences
        print("\n📚 Learning from experiences...")
        experiences = [
            {
                'input': {'task_type': 'computation', 'complexity': 'high'},
                'output': {'success': True, 'duration': 2.5},
                'context': {'time_of_day': 10, 'system_load': 'medium'},
                'reward': 1.0,
                'state': 'processing',
                'action': 'optimize',
                'next_state': 'completed',
                'next_actions': ['report', 'cleanup'],
                'significant': True
            },
            {
                'input': {'task_type': 'communication', 'complexity': 'low'},
                'output': {'success': True, 'duration': 0.8},
                'context': {'time_of_day': 14, 'system_load': 'low'},
                'reward': 0.8,
                'state': 'idle',
                'action': 'respond',
                'next_state': 'communicating',
                'next_actions': ['send', 'wait']
            },
            {
                'input': {'task_type': 'analysis', 'complexity': 'medium'},
                'output': {'success': False, 'duration': 5.0},
                'context': {'time_of_day': 16, 'system_load': 'high'},
                'reward': -0.5,
                'state': 'analyzing',
                'action': 'process',
                'next_state': 'error',
                'next_actions': ['retry', 'abort'],
                'significant': True
            }
        ]

        for i, experience in enumerate(experiences):
            success = await self.learning_manager.learn_from_experience(experience)
            status = "✅" if success else "❌"
            print(f"   {status} Experience {i+1}: {experience['input']['task_type']} task")

        # Get recommendations
        print("\n💡 Getting recommendations...")
        test_contexts = [
            {'task_type': 'computation', 'complexity': 'medium', 'state': 'processing'},
            {'task_type': 'communication', 'complexity': 'high', 'state': 'idle'},
            {'system_load': 'high', 'time_of_day': 16, 'state': 'analyzing'}
        ]

        for i, context in enumerate(test_contexts):
            recommendations = self.learning_manager.get_recommendations(context)
            print(f"   💡 Context {i+1}: {len(recommendations)} recommendations")
            for rec in recommendations[:2]:  # Show top 2
                print(f"      {rec['type']}: {rec['recommendation'][:60]}... (conf: {rec['confidence']:.2f})")

        # Comprehensive stats
        stats = self.learning_manager.get_comprehensive_stats()
        print(f"\n📊 Learning Manager Statistics:")
        print(f"   Agent ID: {stats['agent_id']}")
        print(f"   Learning enabled: {stats['learning_enabled']}")
        print(f"   Adaptation strategy: {stats['adaptation_strategy']}")
        print(f"   Knowledge entries: {stats['knowledge_base']['knowledge_count']}")
        print(f"   Patterns detected: {stats['pattern_recognizer']['total_patterns']}")
        print(f"   ML models: {stats['ml_engine']['models']}")
        print(f"   RL Q-table size: {stats['rl_agent']['q_table_size']}")

    async def _demo_dynamic_learning_agent(self):
        """Dynamic Learning Agent demonstrasyonu"""
        print("\n📋 6. Dynamic Learning Agent - Intelligent Agent Loading")
        print("-" * 50)

        try:
            # Dynamic agent loader'ı al
            loader = get_global_loader()

            # Modülleri tara
            modules = loader.scan_modules()
            print(f"🔍 Scanned modules: {len(modules)} found")

            # Learning agent modülünü yükle
            if "learning_agent" in modules:
                print("🔄 Loading learning agent module...")
                success = loader.load_module("learning_agent")

                if success:
                    print("✅ Learning agent module loaded successfully")

                    # Agent oluştur
                    agent = loader.create_agent(
                        module_name="learning_agent",
                        agent_id="demo_learning_agent_001",
                        config_path="config/agents/learning_agent_dynamic.json"
                    )

                    if agent:
                        print("✅ Learning agent created successfully")
                        self.test_agents.append(agent)

                        # Agent'ı başlat
                        start_success = loader.start_agent("demo_learning_agent_001")
                        if start_success:
                            print("✅ Learning agent started successfully")

                            # Agent ile etkileşim
                            await self._interact_with_learning_agent(agent)
                        else:
                            print("❌ Failed to start learning agent")
                    else:
                        print("❌ Failed to create learning agent")
                else:
                    print("❌ Failed to load learning agent module")
            else:
                print("⚠️ Learning agent module not found")

        except Exception as e:
            print(f"❌ Dynamic agent loading error: {e}")

    async def _interact_with_learning_agent(self, agent):
        """Learning agent ile etkileşim"""
        print("\n🤖 Interacting with learning agent...")

        # Agent'ın learning stats'ını al
        if hasattr(agent, 'get_learning_stats'):
            stats = agent.get_learning_stats()
            print(f"   Agent capabilities: {stats.get('capabilities', [])}")
            print(f"   Learning enabled: {stats.get('learning_system', {}).get('learning_enabled', False)}")

        # Learning task oluştur
        if hasattr(agent, 'create_learning_task'):
            task_id = await agent.create_learning_task('demo_learning', {
                'description': 'Demo learning task for testing',
                'complexity': 'medium',
                'expected_duration': 2.0
            })
            print(f"   ✅ Created learning task: {task_id}")

            # Task'ı çalıştır
            await asyncio.sleep(1.0)
            success = await agent.execute_learning_task(task_id)
            status = "✅" if success else "❌"
            print(f"   {status} Executed learning task: {task_id}")

        # Model eğitimi test et
        if hasattr(agent, 'train_model'):
            print("   🤖 Testing model training...")
            training_success = await agent.train_model("demo_model", "behavioral")
            status = "✅" if training_success else "❌"
            print(f"   {status} Model training: demo_model")

    async def _demo_adaptive_behavior(self):
        """Adaptive Behavior demonstrasyonu"""
        print("\n📋 7. Adaptive Behavior - Performance-Based Adaptation")
        print("-" * 50)

        if not self.learning_manager:
            print("⚠️ Learning manager not initialized, skipping adaptive behavior demo")
            return

        print("🔄 Testing adaptive behavior with performance scenarios...")

        # Scenario 1: Good performance
        print("\n📈 Scenario 1: Good Performance")
        good_metrics = {
            'success_rate': 0.95,
            'avg_execution_time': 1.2,
            'error_rate': 0.02,
            'response_time': 0.8
        }

        adaptation_result = await self.learning_manager.adapt_behavior(good_metrics)
        print(f"   Adaptation needed: {adaptation_result['adaptation_needed']}")
        if adaptation_result['adaptations']:
            print(f"   Adaptations: {adaptation_result['adaptations']}")

        # Scenario 2: Poor performance
        print("\n📉 Scenario 2: Poor Performance")
        poor_metrics = {
            'success_rate': 0.45,
            'avg_execution_time': 8.5,
            'error_rate': 0.25,
            'response_time': 12.0
        }

        adaptation_result = await self.learning_manager.adapt_behavior(poor_metrics)
        print(f"   Adaptation needed: {adaptation_result['adaptation_needed']}")
        if adaptation_result['adaptations']:
            print(f"   Adaptations: {adaptation_result['adaptations']}")

        # Scenario 3: Declining performance trend
        print("\n📊 Scenario 3: Declining Performance Trend")
        declining_metrics = [
            {'success_rate': 0.9, 'response_time': 2.0},
            {'success_rate': 0.8, 'response_time': 3.0},
            {'success_rate': 0.7, 'response_time': 4.0},
            {'success_rate': 0.6, 'response_time': 5.0},
            {'success_rate': 0.5, 'response_time': 6.0}
        ]

        for i, metrics in enumerate(declining_metrics):
            adaptation_result = await self.learning_manager.adapt_behavior(metrics)
            print(f"   Step {i+1}: Success rate {metrics['success_rate']}, "
                  f"Adaptation needed: {adaptation_result['adaptation_needed']}")

        # Show final adaptation statistics
        final_stats = self.learning_manager.get_comprehensive_stats()
        print(f"\n📊 Final Adaptation Statistics:")
        print(f"   Performance history size: {final_stats['performance_history_size']}")
        print(f"   Adaptation history size: {final_stats['adaptation_history_size']}")
        print(f"   Current exploration rate: {final_stats['rl_agent']['exploration_rate']:.3f}")

    async def _cleanup_all(self):
        """Tüm kaynakları temizle"""
        try:
            print("\n🧹 Cleaning up resources...")

            # Dynamic agent'ları durdur
            if self.test_agents:
                loader = get_global_loader()
                for agent in self.test_agents:
                    try:
                        loader.stop_agent(agent.agent_id)
                        print(f"✅ Stopped agent: {agent.agent_id}")
                    except Exception as e:
                        print(f"❌ Stop error for {agent.agent_id}: {e}")

            print("✅ Cleanup completed")

        except Exception as e:
            print(f"❌ Cleanup error: {e}")

    async def interactive_mode(self):
        """İnteraktif mod"""
        print("\n🎮 Interactive Learning Mode")
        print("-" * 50)
        print("Commands:")
        print("  learn <experience_data>       - Add learning experience")
        print("  predict <model> <input>       - Make prediction")
        print("  recommend <context>           - Get recommendations")
        print("  adapt <metrics>               - Trigger adaptation")
        print("  stats                         - Show statistics")
        print("  patterns                      - Show patterns")
        print("  models                        - Show ML models")
        print("  quit                          - Exit")

        if not self.learning_manager:
            print("⚠️ Learning manager not initialized. Run main demo first.")
            return

        while self.running:
            try:
                command = input("\nLearning> ").strip().split()

                if not command:
                    continue

                if command[0] == "quit":
                    break
                elif command[0] == "learn" and len(command) >= 2:
                    experience_str = " ".join(command[1:])
                    await self._interactive_learn(experience_str)
                elif command[0] == "predict" and len(command) >= 3:
                    model_name = command[1]
                    input_str = " ".join(command[2:])
                    self._interactive_predict(model_name, input_str)
                elif command[0] == "recommend" and len(command) >= 2:
                    context_str = " ".join(command[1:])
                    self._interactive_recommend(context_str)
                elif command[0] == "adapt" and len(command) >= 2:
                    metrics_str = " ".join(command[1:])
                    await self._interactive_adapt(metrics_str)
                elif command[0] == "stats":
                    self._interactive_show_stats()
                elif command[0] == "patterns":
                    self._interactive_show_patterns()
                elif command[0] == "models":
                    self._interactive_show_models()
                else:
                    print("Unknown command or invalid syntax")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

    async def _interactive_learn(self, experience_str: str):
        """İnteraktif learning"""
        try:
            # Simple experience parsing
            experience = {
                'input': {'description': experience_str},
                'output': {'success': True},
                'context': {'interactive': True},
                'reward': 1.0
            }

            success = await self.learning_manager.learn_from_experience(experience)
            status = "✅" if success else "❌"
            print(f"{status} Learned from experience: {experience_str}")

        except Exception as e:
            print(f"Learning error: {e}")

    def _interactive_predict(self, model_name: str, input_str: str):
        """İnteraktif prediction"""
        try:
            # Simple input parsing
            input_data = {'description': input_str, 'value': len(input_str)}

            prediction = self.learning_manager.ml_engine.predict(model_name, input_data)
            if prediction:
                print(f"🔮 Prediction: {prediction['prediction']} (confidence: {prediction['confidence']:.3f})")
            else:
                print(f"❌ No prediction available for model: {model_name}")

        except Exception as e:
            print(f"Prediction error: {e}")

    def _interactive_recommend(self, context_str: str):
        """İnteraktif recommendation"""
        try:
            # Simple context parsing
            context = {'description': context_str, 'state': 'interactive'}

            recommendations = self.learning_manager.get_recommendations(context)
            if recommendations:
                print(f"💡 {len(recommendations)} recommendations:")
                for i, rec in enumerate(recommendations):
                    print(f"   {i+1}. {rec['recommendation']} (conf: {rec['confidence']:.2f})")
            else:
                print("💡 No recommendations available")

        except Exception as e:
            print(f"Recommendation error: {e}")

    async def _interactive_adapt(self, metrics_str: str):
        """İnteraktif adaptation"""
        try:
            # Simple metrics parsing
            metrics = {'performance': float(metrics_str) if metrics_str.replace('.', '').isdigit() else 0.5}

            result = await self.learning_manager.adapt_behavior(metrics)
            print(f"🔄 Adaptation result: {result}")

        except Exception as e:
            print(f"Adaptation error: {e}")

    def _interactive_show_stats(self):
        """İnteraktif istatistik gösterme"""
        stats = self.learning_manager.get_comprehensive_stats()
        print(f"\n📊 Learning System Statistics:")
        print(f"   Knowledge entries: {stats['knowledge_base']['knowledge_count']}")
        print(f"   Patterns: {stats['pattern_recognizer']['total_patterns']}")
        print(f"   ML models: {stats['ml_engine']['models']}")
        print(f"   RL Q-table size: {stats['rl_agent']['q_table_size']}")

    def _interactive_show_patterns(self):
        """İnteraktif pattern gösterme"""
        patterns = self.learning_manager.pattern_recognizer.get_frequent_patterns()
        print(f"\n🔍 Detected Patterns ({len(patterns)}):")
        for i, pattern in enumerate(patterns[:5]):
            print(f"   {i+1}. Frequency: {pattern['frequency']}, Signature: {pattern['signature'][:50]}...")

    def _interactive_show_models(self):
        """İnteraktif model gösterme"""
        models = self.learning_manager.ml_engine.list_models()
        print(f"\n🤖 ML Models ({len(models)}):")
        for model in models:
            print(f"   {model['model_name']} ({model['learning_type']})")


async def main():
    """Ana fonksiyon"""
    demo = LearningSystemDemo()

    try:
        # Ana demo'yu çalıştır
        await demo.run_demo()

        # İnteraktif mod (opsiyonel)
        response = input("\n🎮 Enter interactive mode? (y/n): ").strip().lower()
        if response == 'y':
            await demo.interactive_mode()

    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        print("\n🏁 Learning System Demo completed")


if __name__ == "__main__":
    asyncio.run(main())
