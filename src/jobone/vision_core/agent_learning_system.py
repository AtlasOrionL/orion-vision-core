#!/usr/bin/env python3
"""
Agent Learning System - Sprint 3.3
Orion Vision Core - Machine Learning ve Adaptive Behavior Sistemi

Bu modül, agent'ların öğrenme ve adaptasyon yeteneklerini sağlar.
Pattern recognition, reinforcement learning, knowledge base ve
neural network entegrasyonu içerir.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import asyncio
import json
import time
import numpy as np
import pickle
import os
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import threading
import sqlite3
from datetime import datetime, timedelta

# Machine Learning imports
try:
    import sklearn
    from sklearn.cluster import KMeans
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("⚠️ scikit-learn not available. Basic learning features only.")

# Mevcut modüllerini import et
import sys
sys.path.append(os.path.dirname(__file__))

from event_driven_communication import Event, EventType, EventPriority


class LearningType(Enum):
    """Öğrenme tipleri"""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    PATTERN_RECOGNITION = "pattern_recognition"
    BEHAVIORAL = "behavioral"


class AdaptationStrategy(Enum):
    """Adaptasyon stratejileri"""
    IMMEDIATE = "immediate"
    GRADUAL = "gradual"
    THRESHOLD_BASED = "threshold_based"
    TIME_BASED = "time_based"
    PERFORMANCE_BASED = "performance_based"


@dataclass
class LearningData:
    """
    Learning Data Structure

    Öğrenme verilerini saklamak için veri yapısı.
    """
    data_id: str = field(default_factory=lambda: str(int(time.time() * 1000)))
    agent_id: str = ""
    timestamp: float = field(default_factory=time.time)
    learning_type: LearningType = LearningType.BEHAVIORAL
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    labels: List[str] = field(default_factory=list)
    features: List[float] = field(default_factory=list)
    reward: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Learning data'yı dictionary'ye çevir"""
        return {
            'data_id': self.data_id,
            'agent_id': self.agent_id,
            'timestamp': self.timestamp,
            'learning_type': self.learning_type.value,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'context': self.context,
            'performance_metrics': self.performance_metrics,
            'labels': self.labels,
            'features': self.features,
            'reward': self.reward
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningData':
        """Dictionary'den learning data oluştur"""
        return cls(
            data_id=data.get('data_id', str(int(time.time() * 1000))),
            agent_id=data.get('agent_id', ''),
            timestamp=data.get('timestamp', time.time()),
            learning_type=LearningType(data.get('learning_type', LearningType.BEHAVIORAL.value)),
            input_data=data.get('input_data', {}),
            output_data=data.get('output_data', {}),
            context=data.get('context', {}),
            performance_metrics=data.get('performance_metrics', {}),
            labels=data.get('labels', []),
            features=data.get('features', []),
            reward=data.get('reward')
        )


@dataclass
class LearningModel:
    """
    Learning Model Structure

    Öğrenme modellerini saklamak için veri yapısı.
    """
    model_id: str = field(default_factory=lambda: str(int(time.time() * 1000)))
    agent_id: str = ""
    model_name: str = ""
    learning_type: LearningType = LearningType.BEHAVIORAL
    model_data: Optional[bytes] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    performance_history: List[Dict[str, float]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    version: int = 1

    def update_performance(self, metrics: Dict[str, float]):
        """Model performansını güncelle"""
        self.performance_history.append({
            'timestamp': time.time(),
            **metrics
        })
        self.updated_at = time.time()

        # Son 100 performans kaydını tut
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]


class KnowledgeBase:
    """
    Knowledge Base - Agent Bilgi Tabanı

    Agent'ların öğrendikleri bilgileri saklamak ve
    erişmek için bilgi tabanı sistemi.
    """

    def __init__(self, agent_id: str, storage_path: str = "data/knowledge"):
        """
        Knowledge Base başlatıcı

        Args:
            agent_id: Agent'ın benzersiz ID'si
            storage_path: Bilgi tabanının saklanacağı dizin
        """
        self.agent_id = agent_id
        self.storage_path = storage_path
        self.db_path = os.path.join(storage_path, f"{agent_id}_knowledge.db")

        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)

        # Initialize database
        self._init_database()

        # In-memory cache
        self.knowledge_cache: Dict[str, Any] = {}
        self.pattern_cache: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        # Thread safety
        self._lock = threading.RLock()

    def _init_database(self):
        """SQLite veritabanını başlat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Knowledge table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS knowledge (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE NOT NULL,
                        value TEXT NOT NULL,
                        category TEXT,
                        confidence REAL DEFAULT 1.0,
                        created_at REAL NOT NULL,
                        updated_at REAL NOT NULL,
                        access_count INTEGER DEFAULT 0
                    )
                ''')

                # Patterns table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_name TEXT NOT NULL,
                        pattern_data TEXT NOT NULL,
                        frequency INTEGER DEFAULT 1,
                        last_seen REAL NOT NULL,
                        created_at REAL NOT NULL
                    )
                ''')

                # Learning history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS learning_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_id TEXT UNIQUE NOT NULL,
                        learning_data TEXT NOT NULL,
                        created_at REAL NOT NULL
                    )
                ''')

                conn.commit()

        except Exception as e:
            print(f"Database initialization error: {e}")

    def store_knowledge(self, key: str, value: Any, category: str = "general", confidence: float = 1.0):
        """
        Bilgi sakla

        Args:
            key: Bilgi anahtarı
            value: Bilgi değeri
            category: Bilgi kategorisi
            confidence: Güven seviyesi (0.0-1.0)
        """
        with self._lock:
            try:
                value_json = json.dumps(value)
                current_time = time.time()

                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO knowledge
                        (key, value, category, confidence, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (key, value_json, category, confidence, current_time, current_time))
                    conn.commit()

                # Update cache
                self.knowledge_cache[key] = {
                    'value': value,
                    'category': category,
                    'confidence': confidence,
                    'updated_at': current_time
                }

            except Exception as e:
                print(f"Knowledge storage error: {e}")

    def retrieve_knowledge(self, key: str) -> Optional[Any]:
        """
        Bilgi getir

        Args:
            key: Bilgi anahtarı

        Returns:
            Optional[Any]: Bilgi değeri
        """
        with self._lock:
            try:
                # Check cache first
                if key in self.knowledge_cache:
                    return self.knowledge_cache[key]['value']

                # Query database
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT value, category, confidence, updated_at
                        FROM knowledge WHERE key = ?
                    ''', (key,))

                    result = cursor.fetchone()
                    if result:
                        value = json.loads(result[0])

                        # Update cache
                        self.knowledge_cache[key] = {
                            'value': value,
                            'category': result[1],
                            'confidence': result[2],
                            'updated_at': result[3]
                        }

                        # Update access count
                        cursor.execute('''
                            UPDATE knowledge SET access_count = access_count + 1
                            WHERE key = ?
                        ''', (key,))
                        conn.commit()

                        return value

                return None

            except Exception as e:
                print(f"Knowledge retrieval error: {e}")
                return None

    def store_pattern(self, pattern_name: str, pattern_data: Dict[str, Any]):
        """
        Pattern sakla

        Args:
            pattern_name: Pattern adı
            pattern_data: Pattern verisi
        """
        with self._lock:
            try:
                pattern_json = json.dumps(pattern_data)
                current_time = time.time()

                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # Check if pattern exists
                    cursor.execute('''
                        SELECT frequency FROM patterns WHERE pattern_name = ?
                    ''', (pattern_name,))

                    result = cursor.fetchone()
                    if result:
                        # Update existing pattern
                        cursor.execute('''
                            UPDATE patterns SET
                            frequency = frequency + 1,
                            last_seen = ?,
                            pattern_data = ?
                            WHERE pattern_name = ?
                        ''', (current_time, pattern_json, pattern_name))
                    else:
                        # Insert new pattern
                        cursor.execute('''
                            INSERT INTO patterns
                            (pattern_name, pattern_data, last_seen, created_at)
                            VALUES (?, ?, ?, ?)
                        ''', (pattern_name, pattern_json, current_time, current_time))

                    conn.commit()

                # Update cache
                self.pattern_cache[pattern_name].append({
                    'data': pattern_data,
                    'timestamp': current_time
                })

                # Keep only recent patterns in cache
                if len(self.pattern_cache[pattern_name]) > 50:
                    self.pattern_cache[pattern_name] = self.pattern_cache[pattern_name][-50:]

            except Exception as e:
                print(f"Pattern storage error: {e}")

    def get_patterns(self, pattern_name: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Pattern'ları getir

        Args:
            pattern_name: Belirli pattern adı (None ise tümü)
            limit: Maksimum pattern sayısı

        Returns:
            List[Dict]: Pattern listesi
        """
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    if pattern_name:
                        cursor.execute('''
                            SELECT pattern_name, pattern_data, frequency, last_seen
                            FROM patterns WHERE pattern_name = ?
                            ORDER BY frequency DESC LIMIT ?
                        ''', (pattern_name, limit))
                    else:
                        cursor.execute('''
                            SELECT pattern_name, pattern_data, frequency, last_seen
                            FROM patterns ORDER BY frequency DESC LIMIT ?
                        ''', (limit,))

                    results = cursor.fetchall()
                    patterns = []

                    for row in results:
                        patterns.append({
                            'pattern_name': row[0],
                            'pattern_data': json.loads(row[1]),
                            'frequency': row[2],
                            'last_seen': row[3]
                        })

                    return patterns

            except Exception as e:
                print(f"Pattern retrieval error: {e}")
                return []

    def store_learning_data(self, learning_data: LearningData):
        """
        Learning data sakla

        Args:
            learning_data: Öğrenme verisi
        """
        with self._lock:
            try:
                data_json = json.dumps(learning_data.to_dict())

                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO learning_history
                        (data_id, learning_data, created_at)
                        VALUES (?, ?, ?)
                    ''', (learning_data.data_id, data_json, learning_data.timestamp))
                    conn.commit()

            except Exception as e:
                print(f"Learning data storage error: {e}")

    def get_learning_history(self, learning_type: LearningType = None, limit: int = 1000) -> List[LearningData]:
        """
        Learning history getir

        Args:
            learning_type: Belirli öğrenme tipi
            limit: Maksimum kayıt sayısı

        Returns:
            List[LearningData]: Öğrenme verisi listesi
        """
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT learning_data FROM learning_history
                        ORDER BY created_at DESC LIMIT ?
                    ''', (limit,))

                    results = cursor.fetchall()
                    learning_data_list = []

                    for row in results:
                        data_dict = json.loads(row[0])
                        learning_data = LearningData.from_dict(data_dict)

                        if learning_type is None or learning_data.learning_type == learning_type:
                            learning_data_list.append(learning_data)

                    return learning_data_list

            except Exception as e:
                print(f"Learning history retrieval error: {e}")
                return []

    def get_statistics(self) -> Dict[str, Any]:
        """Knowledge base istatistiklerini getir"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()

                    # Knowledge count
                    cursor.execute('SELECT COUNT(*) FROM knowledge')
                    knowledge_count = cursor.fetchone()[0]

                    # Pattern count
                    cursor.execute('SELECT COUNT(*) FROM patterns')
                    pattern_count = cursor.fetchone()[0]

                    # Learning data count
                    cursor.execute('SELECT COUNT(*) FROM learning_history')
                    learning_count = cursor.fetchone()[0]

                    # Most accessed knowledge
                    cursor.execute('''
                        SELECT key, access_count FROM knowledge
                        ORDER BY access_count DESC LIMIT 5
                    ''')
                    top_knowledge = cursor.fetchall()

                    # Most frequent patterns
                    cursor.execute('''
                        SELECT pattern_name, frequency FROM patterns
                        ORDER BY frequency DESC LIMIT 5
                    ''')
                    top_patterns = cursor.fetchall()

                    return {
                        'agent_id': self.agent_id,
                        'knowledge_count': knowledge_count,
                        'pattern_count': pattern_count,
                        'learning_data_count': learning_count,
                        'cache_size': len(self.knowledge_cache),
                        'top_knowledge': [{'key': k, 'access_count': c} for k, c in top_knowledge],
                        'top_patterns': [{'pattern': p, 'frequency': f} for p, f in top_patterns]
                    }

            except Exception as e:
                print(f"Statistics retrieval error: {e}")
                return {'error': str(e)}


class PatternRecognizer:
    """
    Pattern Recognition System

    Agent'ların davranış pattern'larını tanımak ve
    öğrenmek için pattern recognition sistemi.
    """

    def __init__(self, agent_id: str):
        """
        Pattern Recognizer başlatıcı

        Args:
            agent_id: Agent'ın benzersiz ID'si
        """
        self.agent_id = agent_id
        self.patterns: Dict[str, Dict[str, Any]] = {}
        self.sequence_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.temporal_patterns: Dict[str, List[Tuple[float, Dict[str, Any]]]] = defaultdict(list)

        # Pattern detection parameters
        self.min_pattern_frequency = 3
        self.pattern_similarity_threshold = 0.8
        self.temporal_window = 3600  # 1 hour

        # Thread safety
        self._lock = threading.RLock()

    def add_observation(self, observation: Dict[str, Any], timestamp: float = None):
        """
        Gözlem ekle

        Args:
            observation: Gözlem verisi
            timestamp: Zaman damgası
        """
        if timestamp is None:
            timestamp = time.time()

        with self._lock:
            # Extract features from observation
            features = self._extract_features(observation)

            # Update sequence patterns
            self._update_sequence_patterns(features)

            # Update temporal patterns
            self._update_temporal_patterns(features, timestamp)

            # Detect new patterns
            self._detect_patterns(features)

    def _extract_features(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Gözlemden özellik çıkar"""
        features = {}

        for key, value in observation.items():
            if isinstance(value, (int, float)):
                features[f"numeric_{key}"] = value
            elif isinstance(value, str):
                features[f"categorical_{key}"] = value
            elif isinstance(value, bool):
                features[f"boolean_{key}"] = value
            elif isinstance(value, list):
                features[f"list_length_{key}"] = len(value)
                if value and isinstance(value[0], (int, float)):
                    features[f"list_mean_{key}"] = np.mean(value) if value else 0

        return features

    def _update_sequence_patterns(self, features: Dict[str, Any]):
        """Sequence pattern'larını güncelle"""
        # Create feature signature
        signature = self._create_signature(features)

        # Add to sequence
        self.sequence_patterns[self.agent_id].append({
            'signature': signature,
            'features': features,
            'timestamp': time.time()
        })

        # Keep only recent sequences
        max_sequence_length = 100
        if len(self.sequence_patterns[self.agent_id]) > max_sequence_length:
            self.sequence_patterns[self.agent_id] = self.sequence_patterns[self.agent_id][-max_sequence_length:]

    def _update_temporal_patterns(self, features: Dict[str, Any], timestamp: float):
        """Temporal pattern'larını güncelle"""
        # Add temporal observation
        self.temporal_patterns[self.agent_id].append((timestamp, features))

        # Remove old observations outside temporal window
        cutoff_time = timestamp - self.temporal_window
        self.temporal_patterns[self.agent_id] = [
            (t, f) for t, f in self.temporal_patterns[self.agent_id]
            if t >= cutoff_time
        ]

    def _detect_patterns(self, features: Dict[str, Any]):
        """Pattern'ları tespit et"""
        signature = self._create_signature(features)

        # Update pattern frequency
        if signature not in self.patterns:
            self.patterns[signature] = {
                'frequency': 0,
                'first_seen': time.time(),
                'last_seen': time.time(),
                'features': features,
                'variations': []
            }

        pattern = self.patterns[signature]
        pattern['frequency'] += 1
        pattern['last_seen'] = time.time()

        # Store variations
        if len(pattern['variations']) < 10:
            pattern['variations'].append(features)

    def _create_signature(self, features: Dict[str, Any]) -> str:
        """Feature'lardan signature oluştur"""
        # Create a simplified signature for pattern matching
        signature_parts = []

        for key, value in sorted(features.items()):
            if isinstance(value, (int, float)):
                # Quantize numeric values
                quantized = round(value / 10) * 10 if abs(value) > 10 else round(value, 1)
                signature_parts.append(f"{key}:{quantized}")
            else:
                signature_parts.append(f"{key}:{value}")

        return "|".join(signature_parts)

    def get_frequent_patterns(self, min_frequency: int = None) -> List[Dict[str, Any]]:
        """Sık görülen pattern'ları getir"""
        if min_frequency is None:
            min_frequency = self.min_pattern_frequency

        with self._lock:
            frequent_patterns = []

            for signature, pattern in self.patterns.items():
                if pattern['frequency'] >= min_frequency:
                    frequent_patterns.append({
                        'signature': signature,
                        'frequency': pattern['frequency'],
                        'first_seen': pattern['first_seen'],
                        'last_seen': pattern['last_seen'],
                        'features': pattern['features'],
                        'variation_count': len(pattern['variations'])
                    })

            # Sort by frequency
            frequent_patterns.sort(key=lambda x: x['frequency'], reverse=True)
            return frequent_patterns

    def get_temporal_patterns(self, time_window: float = None) -> Dict[str, Any]:
        """Temporal pattern'ları analiz et"""
        if time_window is None:
            time_window = self.temporal_window

        with self._lock:
            current_time = time.time()
            cutoff_time = current_time - time_window

            # Filter recent observations
            recent_observations = [
                (t, f) for t, f in self.temporal_patterns[self.agent_id]
                if t >= cutoff_time
            ]

            if not recent_observations:
                return {'patterns': [], 'statistics': {}}

            # Analyze temporal patterns
            time_intervals = []
            for i in range(1, len(recent_observations)):
                interval = recent_observations[i][0] - recent_observations[i-1][0]
                time_intervals.append(interval)

            statistics = {
                'observation_count': len(recent_observations),
                'time_span': recent_observations[-1][0] - recent_observations[0][0] if recent_observations else 0,
                'average_interval': np.mean(time_intervals) if time_intervals else 0,
                'interval_std': np.std(time_intervals) if time_intervals else 0
            }

            # Detect periodic patterns
            periodic_patterns = self._detect_periodic_patterns(recent_observations)

            return {
                'patterns': periodic_patterns,
                'statistics': statistics,
                'recent_observations': len(recent_observations)
            }

    def _detect_periodic_patterns(self, observations: List[Tuple[float, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Periyodik pattern'ları tespit et"""
        if len(observations) < 3:
            return []

        patterns = []

        # Group observations by hour of day
        hourly_groups = defaultdict(list)
        for timestamp, features in observations:
            hour = datetime.fromtimestamp(timestamp).hour
            hourly_groups[hour].append(features)

        # Find hours with frequent activity
        for hour, hour_features in hourly_groups.items():
            if len(hour_features) >= 2:
                patterns.append({
                    'type': 'hourly',
                    'hour': hour,
                    'frequency': len(hour_features),
                    'pattern': f"Active at hour {hour}"
                })

        return patterns

    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Pattern istatistiklerini getir"""
        with self._lock:
            total_patterns = len(self.patterns)
            frequent_patterns = len([p for p in self.patterns.values() if p['frequency'] >= self.min_pattern_frequency])

            if self.patterns:
                max_frequency = max(p['frequency'] for p in self.patterns.values())
                avg_frequency = np.mean([p['frequency'] for p in self.patterns.values()])
            else:
                max_frequency = 0
                avg_frequency = 0

            return {
                'agent_id': self.agent_id,
                'total_patterns': total_patterns,
                'frequent_patterns': frequent_patterns,
                'max_frequency': max_frequency,
                'average_frequency': avg_frequency,
                'sequence_length': len(self.sequence_patterns[self.agent_id]),
                'temporal_observations': len(self.temporal_patterns[self.agent_id])
            }


class MachineLearningEngine:
    """
    Machine Learning Engine

    Agent'lar için machine learning yetenekleri sağlar.
    Supervised, unsupervised ve reinforcement learning desteği.
    """

    def __init__(self, agent_id: str, storage_path: str = "data/models"):
        """
        ML Engine başlatıcı

        Args:
            agent_id: Agent'ın benzersiz ID'si
            storage_path: Model'lerin saklanacağı dizin
        """
        self.agent_id = agent_id
        self.storage_path = storage_path
        self.models: Dict[str, LearningModel] = {}

        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)

        # ML components
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.classifiers: Dict[str, Any] = {}
        self.clusterers: Dict[str, Any] = {}

        # Thread safety
        self._lock = threading.RLock()

        # Load existing models
        self._load_models()

    def _load_models(self):
        """Mevcut modelleri yükle"""
        try:
            model_file = os.path.join(self.storage_path, f"{self.agent_id}_models.pkl")
            if os.path.exists(model_file):
                with open(model_file, 'rb') as f:
                    self.models = pickle.load(f)
                print(f"Loaded {len(self.models)} models for agent {self.agent_id}")
        except Exception as e:
            print(f"Model loading error: {e}")

    def _save_models(self):
        """Modelleri kaydet"""
        try:
            model_file = os.path.join(self.storage_path, f"{self.agent_id}_models.pkl")
            with open(model_file, 'wb') as f:
                pickle.dump(self.models, f)
        except Exception as e:
            print(f"Model saving error: {e}")

    def train_classifier(self, model_name: str, training_data: List[LearningData],
                        target_feature: str) -> bool:
        """
        Classifier eğit

        Args:
            model_name: Model adı
            training_data: Eğitim verisi
            target_feature: Hedef özellik

        Returns:
            bool: Eğitim başarısı
        """
        if not ML_AVAILABLE:
            print("⚠️ scikit-learn not available for classifier training")
            return False

        with self._lock:
            try:
                # Prepare training data
                X, y = self._prepare_training_data(training_data, target_feature)

                if len(X) < 2:
                    print(f"Insufficient training data: {len(X)} samples")
                    return False

                # Create and train classifier
                classifier = RandomForestClassifier(n_estimators=100, random_state=42)

                # Scale features
                X_scaled = self.scaler.fit_transform(X)

                # Train model
                classifier.fit(X_scaled, y)

                # Create learning model
                model = LearningModel(
                    agent_id=self.agent_id,
                    model_name=model_name,
                    learning_type=LearningType.SUPERVISED,
                    model_data=pickle.dumps({
                        'classifier': classifier,
                        'scaler': self.scaler,
                        'feature_names': [f"feature_{i}" for i in range(len(X[0]))]
                    }),
                    parameters={
                        'target_feature': target_feature,
                        'n_samples': len(X),
                        'n_features': len(X[0]),
                        'n_classes': len(set(y))
                    }
                )

                # Evaluate model
                accuracy = classifier.score(X_scaled, y)
                model.update_performance({'accuracy': accuracy, 'training_samples': len(X)})

                # Store model
                self.models[model_name] = model
                self.classifiers[model_name] = classifier

                # Save models
                self._save_models()

                print(f"✅ Trained classifier '{model_name}' with accuracy: {accuracy:.3f}")
                return True

            except Exception as e:
                print(f"Classifier training error: {e}")
                return False

    def predict(self, model_name: str, input_data: Dict[str, Any]) -> Optional[Any]:
        """
        Prediction yap

        Args:
            model_name: Model adı
            input_data: Girdi verisi

        Returns:
            Optional[Any]: Prediction sonucu
        """
        if not ML_AVAILABLE or model_name not in self.models:
            return None

        with self._lock:
            try:
                model = self.models[model_name]

                # Load model data
                model_components = pickle.loads(model.model_data)
                classifier = model_components['classifier']
                scaler = model_components['scaler']

                # Prepare input features
                features = self._extract_prediction_features(input_data)
                if not features:
                    return None

                # Scale features
                features_scaled = scaler.transform([features])

                # Make prediction
                prediction = classifier.predict(features_scaled)[0]
                confidence = max(classifier.predict_proba(features_scaled)[0])

                # Update model performance
                model.update_performance({
                    'last_prediction': time.time(),
                    'confidence': confidence
                })

                return {
                    'prediction': prediction,
                    'confidence': confidence,
                    'model_name': model_name
                }

            except Exception as e:
                print(f"Prediction error: {e}")
                return None

    def train_clusterer(self, model_name: str, training_data: List[LearningData],
                       n_clusters: int = 5) -> bool:
        """
        Clusterer eğit

        Args:
            model_name: Model adı
            training_data: Eğitim verisi
            n_clusters: Cluster sayısı

        Returns:
            bool: Eğitim başarısı
        """
        if not ML_AVAILABLE:
            print("⚠️ scikit-learn not available for clustering")
            return False

        with self._lock:
            try:
                # Prepare training data
                X = self._prepare_clustering_data(training_data)

                if len(X) < n_clusters:
                    print(f"Insufficient data for clustering: {len(X)} samples, {n_clusters} clusters")
                    return False

                # Create and train clusterer
                clusterer = KMeans(n_clusters=n_clusters, random_state=42)

                # Scale features
                X_scaled = self.scaler.fit_transform(X)

                # Train model
                clusterer.fit(X_scaled)

                # Create learning model
                model = LearningModel(
                    agent_id=self.agent_id,
                    model_name=model_name,
                    learning_type=LearningType.UNSUPERVISED,
                    model_data=pickle.dumps({
                        'clusterer': clusterer,
                        'scaler': self.scaler,
                        'feature_names': [f"feature_{i}" for i in range(len(X[0]))]
                    }),
                    parameters={
                        'n_clusters': n_clusters,
                        'n_samples': len(X),
                        'n_features': len(X[0])
                    }
                )

                # Evaluate model
                inertia = clusterer.inertia_
                model.update_performance({'inertia': inertia, 'training_samples': len(X)})

                # Store model
                self.models[model_name] = model
                self.clusterers[model_name] = clusterer

                # Save models
                self._save_models()

                print(f"✅ Trained clusterer '{model_name}' with {n_clusters} clusters")
                return True

            except Exception as e:
                print(f"Clustering training error: {e}")
                return False

    def _prepare_training_data(self, training_data: List[LearningData],
                              target_feature: str) -> Tuple[List[List[float]], List[Any]]:
        """Eğitim verisini hazırla"""
        X, y = [], []

        for data in training_data:
            if data.features and target_feature in data.output_data:
                X.append(data.features)
                y.append(data.output_data[target_feature])

        return X, y

    def _prepare_clustering_data(self, training_data: List[LearningData]) -> List[List[float]]:
        """Clustering verisi hazırla"""
        X = []

        for data in training_data:
            if data.features:
                X.append(data.features)

        return X

    def _extract_prediction_features(self, input_data: Dict[str, Any]) -> List[float]:
        """Prediction için feature'ları çıkar"""
        features = []

        # Simple feature extraction - can be enhanced
        for key, value in input_data.items():
            if isinstance(value, (int, float)):
                features.append(float(value))
            elif isinstance(value, bool):
                features.append(1.0 if value else 0.0)
            elif isinstance(value, str):
                features.append(float(hash(value) % 1000))  # Simple string hashing

        return features

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Model bilgilerini getir"""
        if model_name not in self.models:
            return None

        model = self.models[model_name]
        return {
            'model_id': model.model_id,
            'model_name': model.model_name,
            'learning_type': model.learning_type.value,
            'parameters': model.parameters,
            'performance_history': model.performance_history[-10:],  # Last 10 records
            'created_at': model.created_at,
            'updated_at': model.updated_at,
            'version': model.version
        }

    def list_models(self) -> List[Dict[str, Any]]:
        """Tüm modelleri listele"""
        return [self.get_model_info(name) for name in self.models.keys()]

    def delete_model(self, model_name: str) -> bool:
        """Model sil"""
        with self._lock:
            if model_name in self.models:
                del self.models[model_name]
                if model_name in self.classifiers:
                    del self.classifiers[model_name]
                if model_name in self.clusterers:
                    del self.clusterers[model_name]

                self._save_models()
                return True
            return False


class ReinforcementLearningAgent:
    """
    Reinforcement Learning Agent

    Q-Learning tabanlı reinforcement learning sistemi.
    Agent'ların deneyimlerinden öğrenmesini sağlar.
    """

    def __init__(self, agent_id: str, learning_rate: float = 0.1,
                 discount_factor: float = 0.9, exploration_rate: float = 0.1):
        """
        RL Agent başlatıcı

        Args:
            agent_id: Agent'ın benzersiz ID'si
            learning_rate: Öğrenme oranı
            discount_factor: İndirim faktörü
            exploration_rate: Keşif oranı (epsilon)
        """
        self.agent_id = agent_id
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate

        # Q-Table: state -> action -> value
        self.q_table: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

        # Experience replay buffer
        self.experience_buffer: deque = deque(maxlen=10000)

        # Learning statistics
        self.learning_stats = {
            'total_episodes': 0,
            'total_rewards': 0.0,
            'average_reward': 0.0,
            'exploration_count': 0,
            'exploitation_count': 0
        }

        # Thread safety
        self._lock = threading.RLock()

    def get_action(self, state: str, available_actions: List[str]) -> str:
        """
        Action seç (epsilon-greedy policy)

        Args:
            state: Mevcut durum
            available_actions: Mevcut aksiyonlar

        Returns:
            str: Seçilen aksiyon
        """
        with self._lock:
            # Epsilon-greedy action selection
            if np.random.random() < self.exploration_rate:
                # Exploration: random action
                action = np.random.choice(available_actions)
                self.learning_stats['exploration_count'] += 1
            else:
                # Exploitation: best known action
                q_values = {action: self.q_table[state][action] for action in available_actions}
                action = max(q_values, key=q_values.get)
                self.learning_stats['exploitation_count'] += 1

            return action

    def update_q_value(self, state: str, action: str, reward: float,
                      next_state: str, next_actions: List[str]):
        """
        Q-value güncelle

        Args:
            state: Mevcut durum
            action: Yapılan aksiyon
            reward: Alınan ödül
            next_state: Sonraki durum
            next_actions: Sonraki mevcut aksiyonlar
        """
        with self._lock:
            # Current Q-value
            current_q = self.q_table[state][action]

            # Maximum Q-value for next state
            if next_actions:
                max_next_q = max(self.q_table[next_state][a] for a in next_actions)
            else:
                max_next_q = 0.0

            # Q-learning update rule
            new_q = current_q + self.learning_rate * (
                reward + self.discount_factor * max_next_q - current_q
            )

            self.q_table[state][action] = new_q

            # Store experience
            experience = {
                'state': state,
                'action': action,
                'reward': reward,
                'next_state': next_state,
                'timestamp': time.time()
            }
            self.experience_buffer.append(experience)

            # Update statistics
            self.learning_stats['total_rewards'] += reward
            self.learning_stats['total_episodes'] += 1

            if self.learning_stats['total_episodes'] > 0:
                self.learning_stats['average_reward'] = (
                    self.learning_stats['total_rewards'] / self.learning_stats['total_episodes']
                )

    def get_q_value(self, state: str, action: str) -> float:
        """Q-value getir"""
        return self.q_table[state][action]

    def get_state_values(self, state: str) -> Dict[str, float]:
        """Durum için tüm action value'larını getir"""
        return dict(self.q_table[state])

    def decay_exploration(self, decay_rate: float = 0.995, min_rate: float = 0.01):
        """Exploration rate'i azalt"""
        self.exploration_rate = max(min_rate, self.exploration_rate * decay_rate)

    def get_learning_statistics(self) -> Dict[str, Any]:
        """Öğrenme istatistiklerini getir"""
        with self._lock:
            return {
                'agent_id': self.agent_id,
                'q_table_size': len(self.q_table),
                'experience_buffer_size': len(self.experience_buffer),
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor,
                'exploration_rate': self.exploration_rate,
                **self.learning_stats
            }


class AgentLearningManager:
    """
    Agent Learning Manager

    Tüm learning bileşenlerini koordine eden ana sınıf.
    Knowledge base, pattern recognition, ML engine ve RL agent'ı yönetir.
    """

    def __init__(self, agent_id: str, config: Dict[str, Any] = None):
        """
        Learning Manager başlatıcı

        Args:
            agent_id: Agent'ın benzersiz ID'si
            config: Konfigürasyon parametreleri
        """
        self.agent_id = agent_id
        self.config = config or {}

        # Learning components
        self.knowledge_base = KnowledgeBase(agent_id)
        self.pattern_recognizer = PatternRecognizer(agent_id)
        self.ml_engine = MachineLearningEngine(agent_id)
        self.rl_agent = ReinforcementLearningAgent(
            agent_id,
            learning_rate=self.config.get('learning_rate', 0.1),
            discount_factor=self.config.get('discount_factor', 0.9),
            exploration_rate=self.config.get('exploration_rate', 0.1)
        )

        # Learning state
        self.learning_enabled = True
        self.adaptation_strategy = AdaptationStrategy(
            self.config.get('adaptation_strategy', AdaptationStrategy.GRADUAL.value)
        )

        # Performance tracking
        self.performance_history: List[Dict[str, Any]] = []
        self.adaptation_history: List[Dict[str, Any]] = []

        # Thread safety
        self._lock = threading.RLock()

        print(f"🧠 Agent Learning Manager initialized for {agent_id}")

    async def learn_from_experience(self, experience: Dict[str, Any]) -> bool:
        """
        Deneyimden öğren

        Args:
            experience: Deneyim verisi

        Returns:
            bool: Öğrenme başarısı
        """
        if not self.learning_enabled:
            return False

        try:
            # Create learning data
            learning_data = LearningData(
                agent_id=self.agent_id,
                learning_type=LearningType.BEHAVIORAL,
                input_data=experience.get('input', {}),
                output_data=experience.get('output', {}),
                context=experience.get('context', {}),
                performance_metrics=experience.get('metrics', {}),
                reward=experience.get('reward')
            )

            # Store in knowledge base
            self.knowledge_base.store_learning_data(learning_data)

            # Add to pattern recognizer
            self.pattern_recognizer.add_observation(experience)

            # Update reinforcement learning
            if 'state' in experience and 'action' in experience:
                self.rl_agent.update_q_value(
                    state=experience['state'],
                    action=experience['action'],
                    reward=experience.get('reward', 0.0),
                    next_state=experience.get('next_state', ''),
                    next_actions=experience.get('next_actions', [])
                )

            # Store knowledge if significant
            if experience.get('significant', False):
                key = f"experience_{int(time.time())}"
                self.knowledge_base.store_knowledge(key, experience, 'experience')

            return True

        except Exception as e:
            print(f"Learning from experience error: {e}")
            return False

    async def adapt_behavior(self, performance_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Davranışı adapt et

        Args:
            performance_metrics: Performans metrikleri

        Returns:
            Dict: Adaptasyon sonuçları
        """
        with self._lock:
            try:
                # Record performance
                self.performance_history.append({
                    'timestamp': time.time(),
                    'metrics': performance_metrics
                })

                # Keep only recent history
                if len(self.performance_history) > 100:
                    self.performance_history = self.performance_history[-100:]

                # Analyze performance trends
                adaptation_needed = self._analyze_performance_trends()

                adaptations = {}

                if adaptation_needed:
                    # Adapt based on strategy
                    if self.adaptation_strategy == AdaptationStrategy.IMMEDIATE:
                        adaptations = await self._immediate_adaptation(performance_metrics)
                    elif self.adaptation_strategy == AdaptationStrategy.GRADUAL:
                        adaptations = await self._gradual_adaptation(performance_metrics)
                    elif self.adaptation_strategy == AdaptationStrategy.THRESHOLD_BASED:
                        adaptations = await self._threshold_based_adaptation(performance_metrics)

                    # Record adaptation
                    self.adaptation_history.append({
                        'timestamp': time.time(),
                        'trigger_metrics': performance_metrics,
                        'adaptations': adaptations
                    })

                return {
                    'adaptation_needed': adaptation_needed,
                    'adaptations': adaptations,
                    'strategy': self.adaptation_strategy.value
                }

            except Exception as e:
                print(f"Behavior adaptation error: {e}")
                return {'error': str(e)}

    def _analyze_performance_trends(self) -> bool:
        """Performans trendlerini analiz et"""
        if len(self.performance_history) < 5:
            return False

        # Simple trend analysis - can be enhanced
        recent_metrics = [p['metrics'] for p in self.performance_history[-5:]]

        # Check if performance is declining
        for metric_name in recent_metrics[0].keys():
            values = [m.get(metric_name, 0) for m in recent_metrics]
            if len(values) >= 3:
                # Simple declining trend detection
                if values[-1] < values[-2] < values[-3]:
                    return True

        return False

    async def _immediate_adaptation(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Immediate adaptation strategy"""
        adaptations = {}

        # Adjust exploration rate based on performance
        if 'success_rate' in metrics:
            if metrics['success_rate'] < 0.5:
                # Increase exploration
                old_rate = self.rl_agent.exploration_rate
                self.rl_agent.exploration_rate = min(0.5, old_rate * 1.2)
                adaptations['exploration_rate'] = {
                    'old': old_rate,
                    'new': self.rl_agent.exploration_rate
                }

        return adaptations

    async def _gradual_adaptation(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Gradual adaptation strategy"""
        adaptations = {}

        # Gradual exploration decay
        self.rl_agent.decay_exploration(decay_rate=0.99)
        adaptations['exploration_decay'] = self.rl_agent.exploration_rate

        return adaptations

    async def _threshold_based_adaptation(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Threshold-based adaptation strategy"""
        adaptations = {}

        # Adapt based on thresholds
        for metric_name, value in metrics.items():
            if metric_name == 'response_time' and value > 5.0:
                # Response time too high
                adaptations['response_optimization'] = True
            elif metric_name == 'error_rate' and value > 0.1:
                # Error rate too high
                adaptations['error_reduction'] = True

        return adaptations

    def get_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Bağlama göre öneriler getir

        Args:
            context: Bağlam bilgisi

        Returns:
            List[Dict]: Öneriler
        """
        recommendations = []

        try:
            # Pattern-based recommendations
            patterns = self.pattern_recognizer.get_frequent_patterns(min_frequency=2)
            for pattern in patterns[:3]:  # Top 3 patterns
                recommendations.append({
                    'type': 'pattern_based',
                    'recommendation': f"Consider pattern: {pattern['signature']}",
                    'confidence': min(1.0, pattern['frequency'] / 10.0),
                    'source': 'pattern_recognizer'
                })

            # ML-based recommendations
            for model_name in self.ml_engine.models.keys():
                prediction = self.ml_engine.predict(model_name, context)
                if prediction:
                    recommendations.append({
                        'type': 'ml_prediction',
                        'recommendation': f"Model {model_name} suggests: {prediction['prediction']}",
                        'confidence': prediction['confidence'],
                        'source': 'ml_engine'
                    })

            # RL-based recommendations
            if 'state' in context:
                state = context['state']
                state_values = self.rl_agent.get_state_values(state)
                if state_values:
                    best_action = max(state_values, key=state_values.get)
                    recommendations.append({
                        'type': 'rl_action',
                        'recommendation': f"Best action for state '{state}': {best_action}",
                        'confidence': min(1.0, abs(state_values[best_action]) / 10.0),
                        'source': 'rl_agent'
                    })

            # Sort by confidence
            recommendations.sort(key=lambda x: x['confidence'], reverse=True)

            return recommendations[:5]  # Top 5 recommendations

        except Exception as e:
            print(f"Recommendation generation error: {e}")
            return []

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Kapsamlı istatistikleri getir"""
        return {
            'agent_id': self.agent_id,
            'learning_enabled': self.learning_enabled,
            'adaptation_strategy': self.adaptation_strategy.value,
            'knowledge_base': self.knowledge_base.get_statistics(),
            'pattern_recognizer': self.pattern_recognizer.get_pattern_statistics(),
            'ml_engine': {
                'models': len(self.ml_engine.models),
                'model_list': [m['model_name'] for m in self.ml_engine.list_models()]
            },
            'rl_agent': self.rl_agent.get_learning_statistics(),
            'performance_history_size': len(self.performance_history),
            'adaptation_history_size': len(self.adaptation_history)
        }
