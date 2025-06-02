#!/usr/bin/env python3
"""
Learning Agent - Sprint 3.3
Orion Vision Core - Machine Learning ve Adaptive Behavior Agent

Bu agent, machine learning ve adaptive behavior yetenekleri ile
deneyimlerinden öğrenen ve davranışını adapte eden gelişmiş bir agent'tır.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import asyncio
import time
import json
import random
import numpy as np
from typing import Dict, Any, List, Optional

# Agent core'u import et
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'jobone', 'vision_core'))

from agent_core import Agent, AgentConfig, AgentStatus
from agent_learning_system import (
    AgentLearningManager, LearningData, LearningType, AdaptationStrategy
)
from communication_agent import OrionMessage, MessageType, MessagePriority
from event_driven_communication import Event, EventType, EventPriority as EventPriority


class LearningAgent(Agent):
    """
    Learning Agent
    
    Machine learning ve adaptive behavior yetenekleri ile
    deneyimlerinden öğrenen gelişmiş agent.
    """
    
    def __init__(self, agent_id: str, config: AgentConfig = None):
        """
        Learning Agent başlatıcı
        
        Args:
            agent_id: Agent'ın benzersiz ID'si
            config: Agent konfigürasyonu
        """
        super().__init__(agent_id, config)
        
        # Learning system
        learning_config = self.config.metadata.get('learning_settings', {}) if self.config else {}
        self.learning_manager = AgentLearningManager(agent_id, learning_config)
        
        # Agent state
        self.current_state = "idle"
        self.available_actions = ["think", "learn", "adapt", "communicate", "analyze"]
        
        # Task management
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[Dict[str, Any]] = []
        self.task_counter = 0
        
        # Learning metrics
        self.learning_metrics = {
            'experiences_processed': 0,
            'adaptations_made': 0,
            'patterns_discovered': 0,
            'models_trained': 0,
            'recommendations_given': 0,
            'success_rate': 0.0,
            'learning_efficiency': 0.0
        }
        
        # Behavior parameters
        self.curiosity_level = learning_config.get('curiosity_level', 0.7)
        self.learning_rate = learning_config.get('learning_rate', 0.1)
        self.adaptation_threshold = learning_config.get('adaptation_threshold', 0.8)
        
        # Agent capabilities
        self.capabilities = [
            "machine_learning",
            "pattern_recognition", 
            "adaptive_behavior",
            "reinforcement_learning",
            "knowledge_management",
            "recommendation_system",
            "experience_learning",
            "behavioral_adaptation"
        ]
        
        print(f"🧠 Learning Agent {agent_id} initialized with learning capabilities")
    
    async def start(self):
        """Agent'ı başlat"""
        await super().start()
        
        # Start learning loops
        asyncio.create_task(self._learning_loop())
        asyncio.create_task(self._adaptation_loop())
        asyncio.create_task(self._exploration_loop())
        
        # Initial learning experience
        await self._record_experience({
            'event': 'agent_started',
            'state': self.current_state,
            'action': 'start',
            'context': {'startup_time': time.time()},
            'reward': 1.0,
            'significant': True
        })
        
        print(f"🚀 Learning Agent {self.agent_id} started with learning enabled")
    
    async def stop(self):
        """Agent'ı durdur"""
        # Record stop experience
        await self._record_experience({
            'event': 'agent_stopped',
            'state': self.current_state,
            'action': 'stop',
            'context': {'stop_time': time.time()},
            'reward': 0.5,
            'significant': True
        })
        
        await super().stop()
        print(f"🛑 Learning Agent {self.agent_id} stopped")
    
    async def process_message(self, message: OrionMessage) -> bool:
        """
        Mesaj işle ve deneyimden öğren
        
        Args:
            message: Gelen mesaj
            
        Returns:
            bool: İşlem başarısı
        """
        try:
            start_time = time.time()
            
            # Process message
            success = await super().process_message(message)
            
            # Record learning experience
            processing_time = time.time() - start_time
            reward = 1.0 if success else -0.5
            
            await self._record_experience({
                'event': 'message_processed',
                'state': self.current_state,
                'action': 'process_message',
                'input': {
                    'message_type': message.message_type,
                    'sender': message.sender_id,
                    'priority': message.priority
                },
                'output': {
                    'success': success,
                    'processing_time': processing_time
                },
                'context': {
                    'message_id': message.message_id,
                    'timestamp': message.timestamp
                },
                'reward': reward,
                'metrics': {
                    'processing_time': processing_time,
                    'success_rate': 1.0 if success else 0.0
                }
            })
            
            # Adapt behavior based on performance
            if random.random() < 0.1:  # 10% chance to adapt
                await self._trigger_adaptation()
            
            return success
            
        except Exception as e:
            print(f"Learning agent message processing error: {e}")
            
            # Record failure experience
            await self._record_experience({
                'event': 'message_processing_failed',
                'state': self.current_state,
                'action': 'process_message',
                'context': {'error': str(e)},
                'reward': -1.0,
                'significant': True
            })
            
            return False
    
    async def create_learning_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """
        Learning task oluştur
        
        Args:
            task_type: Task tipi
            task_data: Task verisi
            
        Returns:
            str: Task ID
        """
        self.task_counter += 1
        task_id = f"{self.agent_id}_learning_task_{self.task_counter}"
        
        task = {
            'task_id': task_id,
            'task_type': task_type,
            'data': task_data,
            'status': 'created',
            'created_at': time.time(),
            'started_at': None,
            'completed_at': None,
            'result': None,
            'learning_applied': False
        }
        
        self.active_tasks[task_id] = task
        
        # Record task creation experience
        await self._record_experience({
            'event': 'task_created',
            'state': self.current_state,
            'action': 'create_task',
            'input': {'task_type': task_type, 'task_data': task_data},
            'context': {'task_id': task_id},
            'reward': 0.5
        })
        
        return task_id
    
    async def execute_learning_task(self, task_id: str) -> bool:
        """
        Learning task'ı çalıştır
        
        Args:
            task_id: Task ID
            
        Returns:
            bool: Çalıştırma başarısı
        """
        if task_id not in self.active_tasks:
            return False
        
        task = self.active_tasks[task_id]
        task['started_at'] = time.time()
        task['status'] = 'running'
        
        try:
            # Get recommendations for task
            context = {
                'task_type': task['task_type'],
                'task_data': task['data'],
                'state': self.current_state
            }
            
            recommendations = self.learning_manager.get_recommendations(context)
            
            # Apply learning to task execution
            if recommendations:
                best_recommendation = recommendations[0]
                task['learning_applied'] = True
                task['applied_recommendation'] = best_recommendation
                
                print(f"🧠 Applied learning: {best_recommendation['recommendation']}")
            
            # Simulate task execution
            execution_time = random.uniform(0.5, 3.0)
            await asyncio.sleep(execution_time)
            
            # Determine success based on learning
            base_success_rate = 0.7
            learning_boost = 0.2 if task['learning_applied'] else 0.0
            success_rate = min(1.0, base_success_rate + learning_boost)
            
            success = random.random() < success_rate
            
            # Complete task
            task['completed_at'] = time.time()
            task['status'] = 'completed' if success else 'failed'
            task['result'] = {
                'success': success,
                'execution_time': execution_time,
                'learning_applied': task['learning_applied']
            }
            
            # Record task execution experience
            reward = 1.0 if success else -0.5
            if task['learning_applied']:
                reward += 0.3  # Bonus for applying learning
            
            await self._record_experience({
                'event': 'task_executed',
                'state': self.current_state,
                'action': 'execute_task',
                'input': {
                    'task_type': task['task_type'],
                    'learning_applied': task['learning_applied']
                },
                'output': {
                    'success': success,
                    'execution_time': execution_time
                },
                'context': {'task_id': task_id},
                'reward': reward,
                'metrics': {
                    'execution_time': execution_time,
                    'success_rate': 1.0 if success else 0.0,
                    'learning_efficiency': 1.0 if task['learning_applied'] else 0.0
                }
            })
            
            # Move to completed tasks
            self.completed_tasks.append(task)
            del self.active_tasks[task_id]
            
            # Update metrics
            self.learning_metrics['experiences_processed'] += 1
            if task['learning_applied']:
                self.learning_metrics['learning_efficiency'] = (
                    self.learning_metrics['learning_efficiency'] * 0.9 + 
                    (1.0 if success else 0.0) * 0.1
                )
            
            return success
            
        except Exception as e:
            print(f"Task execution error: {e}")
            
            task['status'] = 'error'
            task['completed_at'] = time.time()
            task['result'] = {'error': str(e)}
            
            # Record error experience
            await self._record_experience({
                'event': 'task_execution_failed',
                'state': self.current_state,
                'action': 'execute_task',
                'context': {'task_id': task_id, 'error': str(e)},
                'reward': -1.0,
                'significant': True
            })
            
            return False
    
    async def train_model(self, model_name: str, training_data_type: str) -> bool:
        """
        Model eğit
        
        Args:
            model_name: Model adı
            training_data_type: Eğitim verisi tipi
            
        Returns:
            bool: Eğitim başarısı
        """
        try:
            # Get learning history for training
            learning_history = self.learning_manager.knowledge_base.get_learning_history(
                learning_type=LearningType.BEHAVIORAL,
                limit=100
            )
            
            if len(learning_history) < 10:
                print(f"Insufficient training data: {len(learning_history)} samples")
                return False
            
            # Train classifier
            success = self.learning_manager.ml_engine.train_classifier(
                model_name=model_name,
                training_data=learning_history,
                target_feature='success'
            )
            
            if success:
                self.learning_metrics['models_trained'] += 1
                
                # Record training experience
                await self._record_experience({
                    'event': 'model_trained',
                    'state': self.current_state,
                    'action': 'train_model',
                    'input': {
                        'model_name': model_name,
                        'training_samples': len(learning_history)
                    },
                    'output': {'success': True},
                    'reward': 2.0,
                    'significant': True
                })
                
                print(f"✅ Successfully trained model: {model_name}")
            
            return success
            
        except Exception as e:
            print(f"Model training error: {e}")
            return False
    
    async def _record_experience(self, experience: Dict[str, Any]):
        """Deneyimi kaydet ve öğren"""
        try:
            # Add agent context
            experience['agent_id'] = self.agent_id
            experience['timestamp'] = time.time()
            
            # Learn from experience
            await self.learning_manager.learn_from_experience(experience)
            
            # Update state if provided
            if 'next_state' in experience:
                self.current_state = experience['next_state']
            
        except Exception as e:
            print(f"Experience recording error: {e}")
    
    async def _trigger_adaptation(self):
        """Adaptasyon tetikle"""
        try:
            # Calculate current performance metrics
            recent_tasks = self.completed_tasks[-10:] if self.completed_tasks else []
            
            if recent_tasks:
                success_rate = sum(1 for t in recent_tasks if t['result'].get('success', False)) / len(recent_tasks)
                avg_execution_time = np.mean([t['result'].get('execution_time', 0) for t in recent_tasks])
                
                performance_metrics = {
                    'success_rate': success_rate,
                    'avg_execution_time': avg_execution_time,
                    'task_count': len(recent_tasks)
                }
                
                # Trigger adaptation
                adaptation_result = await self.learning_manager.adapt_behavior(performance_metrics)
                
                if adaptation_result.get('adaptation_needed', False):
                    self.learning_metrics['adaptations_made'] += 1
                    
                    print(f"🔄 Adaptation triggered: {adaptation_result['adaptations']}")
                    
                    # Record adaptation experience
                    await self._record_experience({
                        'event': 'behavior_adapted',
                        'state': self.current_state,
                        'action': 'adapt_behavior',
                        'input': performance_metrics,
                        'output': adaptation_result,
                        'reward': 1.0,
                        'significant': True
                    })
        
        except Exception as e:
            print(f"Adaptation trigger error: {e}")
    
    async def _learning_loop(self):
        """Learning döngüsü"""
        while self.running:
            try:
                # Periodic learning activities
                if random.random() < self.curiosity_level:
                    # Explore patterns
                    patterns = self.learning_manager.pattern_recognizer.get_frequent_patterns()
                    if patterns:
                        self.learning_metrics['patterns_discovered'] = len(patterns)
                        
                        # Record pattern discovery
                        await self._record_experience({
                            'event': 'patterns_discovered',
                            'state': self.current_state,
                            'action': 'explore_patterns',
                            'output': {'pattern_count': len(patterns)},
                            'reward': 0.5 * len(patterns)
                        })
                
                # Sleep for learning interval
                await asyncio.sleep(60.0)  # 1 minute
                
            except Exception as e:
                print(f"Learning loop error: {e}")
                await asyncio.sleep(10.0)
    
    async def _adaptation_loop(self):
        """Adaptation döngüsü"""
        while self.running:
            try:
                # Periodic adaptation check
                if len(self.completed_tasks) >= 5:
                    await self._trigger_adaptation()
                
                # Sleep for adaptation interval
                await asyncio.sleep(300.0)  # 5 minutes
                
            except Exception as e:
                print(f"Adaptation loop error: {e}")
                await asyncio.sleep(30.0)
    
    async def _exploration_loop(self):
        """Exploration döngüsü"""
        while self.running:
            try:
                # Explore new actions occasionally
                if random.random() < 0.1:  # 10% chance
                    action = random.choice(self.available_actions)
                    
                    # Record exploration
                    await self._record_experience({
                        'event': 'exploration',
                        'state': self.current_state,
                        'action': action,
                        'context': {'exploration': True},
                        'reward': 0.1
                    })
                
                # Sleep for exploration interval
                await asyncio.sleep(120.0)  # 2 minutes
                
            except Exception as e:
                print(f"Exploration loop error: {e}")
                await asyncio.sleep(15.0)
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Learning istatistiklerini getir"""
        base_stats = self.get_stats()
        learning_stats = self.learning_manager.get_comprehensive_stats()
        
        return {
            **base_stats,
            'learning_metrics': self.learning_metrics,
            'learning_system': learning_stats,
            'current_state': self.current_state,
            'available_actions': self.available_actions,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'capabilities': self.capabilities,
            'behavior_parameters': {
                'curiosity_level': self.curiosity_level,
                'learning_rate': self.learning_rate,
                'adaptation_threshold': self.adaptation_threshold
            }
        }
