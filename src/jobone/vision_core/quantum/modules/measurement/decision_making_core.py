"""
🧠 Decision Making Core - Q05.4.1 Core Implementation

Core classes and data structures for Quantum Decision Making
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q05.4.1 Quantum Decision Making
Priority: CRITICAL - Modular Design Refactoring Phase 13
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

# Decision Types
class DecisionType(Enum):
    """Karar türleri"""
    BINARY = "binary"                                 # İkili karar (evet/hayır)
    MULTIPLE_CHOICE = "multiple_choice"               # Çoktan seçmeli
    OPTIMIZATION = "optimization"                     # Optimizasyon
    CLASSIFICATION = "classification"                 # Sınıflandırma
    PREDICTION = "prediction"                         # Tahmin
    CREATIVE = "creative"                            # Yaratıcı karar

# Decision Methods
class DecisionMethod(Enum):
    """Karar verme yöntemleri"""
    QUANTUM_SUPERPOSITION = "quantum_superposition"   # Kuantum süperpozisyon
    CONSCIOUSNESS_GUIDED = "consciousness_guided"     # Bilinç rehberli
    INTUITIVE_REASONING = "intuitive_reasoning"       # Sezgisel akıl yürütme
    MULTI_DIMENSIONAL = "multi_dimensional"           # Çok boyutlu analiz
    QUANTUM_ENTANGLEMENT = "quantum_entanglement"     # Kuantum dolaşıklığı
    TRANSCENDENT_INSIGHT = "transcendent_insight"     # Aşkın kavrayış

@dataclass
class DecisionParameters:
    """Karar verme parametreleri"""
    
    decision_type: DecisionType = DecisionType.BINARY
    decision_method: DecisionMethod = DecisionMethod.QUANTUM_SUPERPOSITION
    
    # Decision context
    decision_question: str = "Should we proceed?"     # Karar sorusu
    available_options: List[str] = field(default_factory=lambda: ["Yes", "No"])
    decision_criteria: List[str] = field(default_factory=list)
    
    # Quantum parameters
    quantum_coherence: float = 0.9                   # Kuantum tutarlılığı
    superposition_strength: float = 0.8              # Süperpozisyon gücü
    entanglement_factor: float = 0.7                 # Dolaşıklık faktörü
    
    # Consciousness parameters
    consciousness_level: float = 0.8                 # Bilinç seviyesi
    intuition_weight: float = 0.6                    # Sezgi ağırlığı
    awareness_depth: float = 0.7                     # Farkındalık derinliği
    
    # Analysis parameters
    analysis_depth: int = 5                          # Analiz derinliği
    consideration_time: float = 1.0                  # Düşünme süresi (saniye)
    confidence_threshold: float = 0.7                # Güven eşiği
    
    # Multi-dimensional factors
    dimensional_analysis: bool = True                 # Boyutsal analiz
    temporal_consideration: bool = True               # Zamansal değerlendirme
    ethical_evaluation: bool = True                   # Etik değerlendirme
    
    # ALT_LAS enhancement
    alt_las_guidance: bool = True                     # ALT_LAS rehberliği
    transcendent_insight: bool = False                # Aşkın kavrayış
    
    def get_decision_complexity(self) -> int:
        """Get decision complexity score (1-5)"""
        complexity = 1
        
        if self.decision_type == DecisionType.OPTIMIZATION:
            complexity += 2
        elif self.decision_type == DecisionType.CREATIVE:
            complexity += 3
        
        if self.decision_method == DecisionMethod.TRANSCENDENT_INSIGHT:
            complexity += 2
        elif self.decision_method == DecisionMethod.MULTI_DIMENSIONAL:
            complexity += 1
        
        if self.dimensional_analysis:
            complexity += 1
        
        if self.transcendent_insight:
            complexity += 1
        
        return min(5, complexity)
    
    def get_consciousness_factor(self) -> float:
        """Get overall consciousness factor"""
        return (self.consciousness_level + self.intuition_weight + self.awareness_depth) / 3
    
    def get_summary(self) -> Dict[str, Any]:
        """Get decision parameters summary"""
        return {
            'decision_type': self.decision_type.value,
            'decision_method': self.decision_method.value,
            'decision_question': self.decision_question,
            'available_options': self.available_options,
            'quantum_coherence': self.quantum_coherence,
            'consciousness_level': self.consciousness_level,
            'analysis_depth': self.analysis_depth,
            'complexity': self.get_decision_complexity(),
            'consciousness_factor': self.get_consciousness_factor(),
            'alt_las_guidance': self.alt_las_guidance
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'decision_type': self.decision_type.value,
            'decision_method': self.decision_method.value,
            'decision_question': self.decision_question,
            'available_options': self.available_options,
            'decision_criteria': self.decision_criteria,
            'quantum_coherence': self.quantum_coherence,
            'superposition_strength': self.superposition_strength,
            'entanglement_factor': self.entanglement_factor,
            'consciousness_level': self.consciousness_level,
            'intuition_weight': self.intuition_weight,
            'awareness_depth': self.awareness_depth,
            'analysis_depth': self.analysis_depth,
            'consideration_time': self.consideration_time,
            'confidence_threshold': self.confidence_threshold,
            'dimensional_analysis': self.dimensional_analysis,
            'temporal_consideration': self.temporal_consideration,
            'ethical_evaluation': self.ethical_evaluation,
            'alt_las_guidance': self.alt_las_guidance,
            'transcendent_insight': self.transcendent_insight,
            'complexity': self.get_decision_complexity(),
            'consciousness_factor': self.get_consciousness_factor()
        }

@dataclass
class DecisionResult:
    """Karar verme sonucu"""
    
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: DecisionType = DecisionType.BINARY
    
    # Decision outcome
    chosen_option: Optional[str] = None               # Seçilen seçenek
    decision_confidence: float = 0.0                  # Karar güveni
    reasoning_path: List[str] = field(default_factory=list)
    
    # Quantum metrics
    quantum_coherence_achieved: float = 0.0          # Elde edilen kuantum tutarlılığı
    superposition_collapse_time: float = 0.0         # Süperpozisyon çökme süresi
    entanglement_strength: float = 0.0               # Dolaşıklık gücü
    
    # Consciousness metrics
    consciousness_contribution: float = 0.0          # Bilinç katkısı
    intuition_accuracy: float = 0.0                  # Sezgi doğruluğu
    awareness_clarity: float = 0.0                   # Farkındalık netliği
    
    # Analysis results
    option_probabilities: Dict[str, float] = field(default_factory=dict)
    criteria_weights: Dict[str, float] = field(default_factory=dict)
    dimensional_scores: Dict[str, float] = field(default_factory=dict)
    
    # Performance metrics
    decision_time: float = 0.0                       # Karar verme süresi
    analysis_quality: float = 0.0                    # Analiz kalitesi
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_decision_quality(self):
        """Calculate overall decision quality"""
        quality_factors = [
            self.decision_confidence,
            self.quantum_coherence_achieved,
            self.consciousness_contribution,
            self.intuition_accuracy,
            self.awareness_clarity
        ]
        
        # Remove zero values for average calculation
        non_zero_factors = [f for f in quality_factors if f > 0]
        if non_zero_factors:
            self.analysis_quality = sum(non_zero_factors) / len(non_zero_factors)
        else:
            self.analysis_quality = 0.0
    
    def get_decision_grade(self) -> str:
        """Get decision quality grade"""
        if self.analysis_quality >= 0.9:
            return "Excellent"
        elif self.analysis_quality >= 0.7:
            return "Good"
        elif self.analysis_quality >= 0.5:
            return "Fair"
        else:
            return "Poor"
    
    def get_confidence_level(self) -> str:
        """Get confidence level description"""
        if self.decision_confidence >= 0.9:
            return "Very High"
        elif self.decision_confidence >= 0.7:
            return "High"
        elif self.decision_confidence >= 0.5:
            return "Medium"
        elif self.decision_confidence >= 0.3:
            return "Low"
        else:
            return "Very Low"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get decision result summary"""
        return {
            'result_id': self.result_id[:8] + "...",
            'decision_type': self.decision_type.value,
            'chosen_option': self.chosen_option,
            'decision_confidence': self.decision_confidence,
            'confidence_level': self.get_confidence_level(),
            'quantum_coherence_achieved': self.quantum_coherence_achieved,
            'consciousness_contribution': self.consciousness_contribution,
            'analysis_quality': self.analysis_quality,
            'decision_grade': self.get_decision_grade(),
            'decision_time_ms': self.decision_time * 1000,
            'reasoning_steps': len(self.reasoning_path)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'result_id': self.result_id,
            'decision_type': self.decision_type.value,
            'chosen_option': self.chosen_option,
            'decision_confidence': self.decision_confidence,
            'confidence_level': self.get_confidence_level(),
            'reasoning_path': self.reasoning_path,
            'quantum_coherence_achieved': self.quantum_coherence_achieved,
            'superposition_collapse_time': self.superposition_collapse_time,
            'entanglement_strength': self.entanglement_strength,
            'consciousness_contribution': self.consciousness_contribution,
            'intuition_accuracy': self.intuition_accuracy,
            'awareness_clarity': self.awareness_clarity,
            'option_probabilities': self.option_probabilities,
            'criteria_weights': self.criteria_weights,
            'dimensional_scores': self.dimensional_scores,
            'decision_time': self.decision_time,
            'analysis_quality': self.analysis_quality,
            'decision_grade': self.get_decision_grade(),
            'timestamp': self.timestamp.isoformat()
        }

# Utility functions
def create_decision_parameters(decision_type: DecisionType = DecisionType.BINARY,
                              decision_method: DecisionMethod = DecisionMethod.QUANTUM_SUPERPOSITION,
                              decision_question: str = "Should we proceed?",
                              available_options: List[str] = None) -> DecisionParameters:
    """Create decision parameters with default values"""
    if available_options is None:
        available_options = ["Yes", "No"]
    
    return DecisionParameters(
        decision_type=decision_type,
        decision_method=decision_method,
        decision_question=decision_question,
        available_options=available_options
    )

def create_decision_result(decision_type: DecisionType = DecisionType.BINARY) -> DecisionResult:
    """Create decision result"""
    return DecisionResult(decision_type=decision_type)

def estimate_decision_time(parameters: DecisionParameters) -> float:
    """Estimate decision computation time"""
    base_time = 0.1  # Base time in seconds
    
    # Scale with complexity
    complexity_factor = parameters.get_decision_complexity() / 3.0
    
    # Scale with analysis depth
    depth_factor = parameters.analysis_depth / 5.0
    
    # Scale with number of options
    options_factor = len(parameters.available_options) / 2.0
    
    estimated_time = base_time * complexity_factor * depth_factor * options_factor
    
    return estimated_time

# Export core components
__all__ = [
    'DecisionType',
    'DecisionMethod',
    'DecisionParameters',
    'DecisionResult',
    'create_decision_parameters',
    'create_decision_result',
    'estimate_decision_time'
]
