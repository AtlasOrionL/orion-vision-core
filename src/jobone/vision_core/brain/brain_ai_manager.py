#!/usr/bin/env python3
"""
Brain AI Manager - Advanced AI Task Optimization and Message Processing
Sprint 8.2 - Advanced LLM Management and Core "Brain" AI Capabilities
Orion Vision Core - Autonomous AI Operating System

This module provides advanced AI capabilities including task analysis,
message fragmentation, and intelligent processing optimization for the
Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.2.0
Date: 30 Mayıs 2025
"""

import logging
import asyncio
import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from ..llm.llm_api_manager import get_llm_api_manager, ModelCapability
from ..llm.model_selector import get_model_selector, TaskRequirements, TaskComplexity, SelectionStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BrainAIManager")

class TaskType(Enum):
    """AI task type enumeration"""
    CONVERSATION = "conversation"
    ANALYSIS = "analysis"
    CODE_GENERATION = "code_generation"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    REASONING = "reasoning"
    CREATIVE_WRITING = "creative_writing"
    PROBLEM_SOLVING = "problem_solving"

class MessageFragmentType(Enum):
    """Message fragment type enumeration"""
    CONTEXT = "context"
    INSTRUCTION = "instruction"
    DATA = "data"
    EXAMPLE = "example"
    CONSTRAINT = "constraint"

@dataclass
class MessageFragment:
    """Message fragment data structure"""
    fragment_id: str
    fragment_type: MessageFragmentType
    content: str
    priority: int
    token_estimate: int
    dependencies: List[str]

@dataclass
class TaskAnalysis:
    """Task analysis result"""
    task_id: str
    task_type: TaskType
    complexity: TaskComplexity
    estimated_tokens: int
    recommended_model: str
    confidence: float
    reasoning: str
    optimization_suggestions: List[str]

class BrainAIManager(QObject):
    """
    Advanced AI brain management system.
    
    Features:
    - Intelligent task analysis and decomposition
    - Message fragmentation for large contexts
    - Optimal model selection and routing
    - Context management and optimization
    - Learning from task execution results
    - Performance optimization strategies
    """
    
    # Signals
    task_analyzed = pyqtSignal(dict)  # TaskAnalysis as dict
    message_fragmented = pyqtSignal(str, list)  # original_message, fragments
    optimization_applied = pyqtSignal(str, dict)  # optimization_type, details
    learning_updated = pyqtSignal(dict)  # learning_metrics
    
    def __init__(self):
        """Initialize Brain AI Manager"""
        super().__init__()
        
        # Component references
        self.llm_manager = get_llm_api_manager()
        self.model_selector = get_model_selector()
        
        # Task analysis
        self.task_patterns = {
            TaskType.CONVERSATION: [
                r'\b(hello|hi|hey|chat|talk|discuss)\b',
                r'\b(how are you|what\'s up|tell me about)\b'
            ],
            TaskType.ANALYSIS: [
                r'\b(analyze|examine|evaluate|assess|review)\b',
                r'\b(what does this mean|explain|interpret)\b'
            ],
            TaskType.CODE_GENERATION: [
                r'\b(write code|create function|implement|program)\b',
                r'\b(python|javascript|java|c\+\+|html|css)\b'
            ],
            TaskType.SUMMARIZATION: [
                r'\b(summarize|summary|brief|overview|tldr)\b',
                r'\b(key points|main ideas|highlights)\b'
            ],
            TaskType.TRANSLATION: [
                r'\b(translate|translation|convert to)\b',
                r'\b(in turkish|in english|in spanish|in french)\b'
            ],
            TaskType.REASONING: [
                r'\b(why|because|reason|logic|prove|deduce)\b',
                r'\b(if.*then|therefore|consequently)\b'
            ],
            TaskType.CREATIVE_WRITING: [
                r'\b(write story|create poem|generate text)\b',
                r'\b(creative|imaginative|fictional)\b'
            ],
            TaskType.PROBLEM_SOLVING: [
                r'\b(solve|solution|fix|resolve|troubleshoot)\b',
                r'\b(problem|issue|challenge|difficulty)\b'
            ]
        }
        
        # Message fragmentation
        self.max_fragment_tokens = 2000
        self.fragment_overlap_tokens = 100
        self.fragment_counter = 0
        
        # Learning and optimization
        self.task_performance_history: Dict[str, List[Dict[str, Any]]] = {}
        self.optimization_strategies: Dict[str, Callable] = {}
        self.learning_metrics = {
            'tasks_analyzed': 0,
            'messages_fragmented': 0,
            'optimizations_applied': 0,
            'average_accuracy': 0.0,
            'performance_improvements': 0
        }
        
        # Context management
        self.active_contexts: Dict[str, Dict[str, Any]] = {}
        self.context_memory_limit = 10000  # tokens
        
        # Performance monitoring
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self._update_performance_metrics)
        self.performance_timer.start(60000)  # Update every minute
        
        # Initialize optimization strategies
        self._initialize_optimization_strategies()
        
        logger.info("🧠 Brain AI Manager initialized")
    
    def _initialize_optimization_strategies(self):
        """Initialize optimization strategies"""
        self.optimization_strategies = {
            'context_compression': self._optimize_context_compression,
            'model_routing': self._optimize_model_routing,
            'message_chunking': self._optimize_message_chunking,
            'parallel_processing': self._optimize_parallel_processing
        }
        
        logger.info(f"🧠 Initialized {len(self.optimization_strategies)} optimization strategies")
    
    def analyze_task(self, message: str, context: Optional[Dict[str, Any]] = None) -> TaskAnalysis:
        """
        Analyze task requirements and provide optimization recommendations.
        
        Args:
            message: Input message to analyze
            context: Optional context information
            
        Returns:
            TaskAnalysis with recommendations
        """
        try:
            task_id = self._generate_task_id()
            
            # Classify task type
            task_type = self._classify_task_type(message)
            
            # Estimate complexity
            complexity = self._estimate_task_complexity(message, task_type)
            
            # Estimate token requirements
            estimated_tokens = self._estimate_token_requirements(message, context)
            
            # Select optimal model
            task_requirements = TaskRequirements(
                capability=self._task_type_to_capability(task_type),
                complexity=complexity,
                max_tokens=estimated_tokens,
                max_cost_per_token=None,
                max_response_time=None,
                prefer_local=False,
                quality_threshold=0.7
            )
            
            recommended_model = self.model_selector.select_model(task_requirements)
            
            # Calculate confidence
            confidence = self._calculate_analysis_confidence(message, task_type, complexity)
            
            # Generate reasoning
            reasoning = self._generate_analysis_reasoning(task_type, complexity, recommended_model)
            
            # Generate optimization suggestions
            optimization_suggestions = self._generate_optimization_suggestions(
                message, task_type, complexity, estimated_tokens
            )
            
            # Create task analysis
            analysis = TaskAnalysis(
                task_id=task_id,
                task_type=task_type,
                complexity=complexity,
                estimated_tokens=estimated_tokens,
                recommended_model=recommended_model or "fallback",
                confidence=confidence,
                reasoning=reasoning,
                optimization_suggestions=optimization_suggestions
            )
            
            # Update learning metrics
            self.learning_metrics['tasks_analyzed'] += 1
            
            # Emit signal
            self.task_analyzed.emit(self._task_analysis_to_dict(analysis))
            
            logger.info(f"🧠 Analyzed task: {task_type.value} (complexity: {complexity.value})")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing task: {e}")
            # Return fallback analysis
            return TaskAnalysis(
                task_id=self._generate_task_id(),
                task_type=TaskType.CONVERSATION,
                complexity=TaskComplexity.SIMPLE,
                estimated_tokens=len(message.split()) * 2,
                recommended_model="fallback",
                confidence=0.5,
                reasoning="Fallback analysis due to error",
                optimization_suggestions=[]
            )
    
    def fragment_message(self, message: str, max_tokens: int = None) -> List[MessageFragment]:
        """
        Fragment large message into manageable chunks.
        
        Args:
            message: Message to fragment
            max_tokens: Maximum tokens per fragment
            
        Returns:
            List of message fragments
        """
        try:
            if max_tokens is None:
                max_tokens = self.max_fragment_tokens
            
            # Estimate total tokens
            total_tokens = len(message.split()) * 1.3  # Rough estimate
            
            if total_tokens <= max_tokens:
                # No fragmentation needed
                fragment = MessageFragment(
                    fragment_id=self._generate_fragment_id(),
                    fragment_type=MessageFragmentType.INSTRUCTION,
                    content=message,
                    priority=1,
                    token_estimate=int(total_tokens),
                    dependencies=[]
                )
                return [fragment]
            
            # Fragment the message
            fragments = self._create_message_fragments(message, max_tokens)
            
            # Update learning metrics
            self.learning_metrics['messages_fragmented'] += 1
            
            # Emit signal
            self.message_fragmented.emit(message, [self._fragment_to_dict(f) for f in fragments])
            
            logger.info(f"🧠 Fragmented message into {len(fragments)} parts")
            return fragments
            
        except Exception as e:
            logger.error(f"❌ Error fragmenting message: {e}")
            return []
    
    def _classify_task_type(self, message: str) -> TaskType:
        """Classify task type based on message content"""
        message_lower = message.lower()
        
        # Score each task type
        task_scores = {}
        for task_type, patterns in self.task_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, message_lower, re.IGNORECASE))
                score += matches
            task_scores[task_type] = score
        
        # Return highest scoring task type
        if task_scores:
            best_task = max(task_scores, key=task_scores.get)
            if task_scores[best_task] > 0:
                return best_task
        
        # Default to conversation
        return TaskType.CONVERSATION
    
    def _estimate_task_complexity(self, message: str, task_type: TaskType) -> TaskComplexity:
        """Estimate task complexity based on message and type"""
        message_length = len(message.split())
        
        # Base complexity on message length
        if message_length < 20:
            base_complexity = TaskComplexity.SIMPLE
        elif message_length < 100:
            base_complexity = TaskComplexity.MODERATE
        elif message_length < 500:
            base_complexity = TaskComplexity.COMPLEX
        else:
            base_complexity = TaskComplexity.EXPERT
        
        # Adjust based on task type
        complexity_adjustments = {
            TaskType.CONVERSATION: 0,
            TaskType.ANALYSIS: 1,
            TaskType.CODE_GENERATION: 1,
            TaskType.SUMMARIZATION: 0,
            TaskType.TRANSLATION: 0,
            TaskType.REASONING: 2,
            TaskType.CREATIVE_WRITING: 1,
            TaskType.PROBLEM_SOLVING: 2
        }
        
        adjustment = complexity_adjustments.get(task_type, 0)
        complexity_levels = list(TaskComplexity)
        current_index = complexity_levels.index(base_complexity)
        new_index = min(len(complexity_levels) - 1, current_index + adjustment)
        
        return complexity_levels[new_index]
    
    def _estimate_token_requirements(self, message: str, context: Optional[Dict[str, Any]]) -> int:
        """Estimate token requirements for the task"""
        # Base tokens from message
        base_tokens = len(message.split()) * 1.3
        
        # Add context tokens
        context_tokens = 0
        if context:
            context_str = str(context)
            context_tokens = len(context_str.split()) * 1.3
        
        # Estimate response tokens (typically 2-3x input)
        response_multiplier = 2.5
        
        total_tokens = (base_tokens + context_tokens) * response_multiplier
        
        return int(total_tokens)
    
    def _task_type_to_capability(self, task_type: TaskType) -> ModelCapability:
        """Convert task type to model capability"""
        mapping = {
            TaskType.CONVERSATION: ModelCapability.CONVERSATION,
            TaskType.ANALYSIS: ModelCapability.ANALYSIS,
            TaskType.CODE_GENERATION: ModelCapability.CODE_GENERATION,
            TaskType.SUMMARIZATION: ModelCapability.SUMMARIZATION,
            TaskType.TRANSLATION: ModelCapability.TRANSLATION,
            TaskType.REASONING: ModelCapability.REASONING,
            TaskType.CREATIVE_WRITING: ModelCapability.TEXT_GENERATION,
            TaskType.PROBLEM_SOLVING: ModelCapability.REASONING
        }
        
        return mapping.get(task_type, ModelCapability.TEXT_GENERATION)
    
    def _calculate_analysis_confidence(self, message: str, task_type: TaskType, 
                                     complexity: TaskComplexity) -> float:
        """Calculate confidence in task analysis"""
        # Base confidence
        confidence = 0.8
        
        # Adjust based on message clarity
        if len(message.split()) < 5:
            confidence -= 0.2  # Very short messages are ambiguous
        
        # Adjust based on task type detection strength
        message_lower = message.lower()
        patterns = self.task_patterns.get(task_type, [])
        pattern_matches = sum(len(re.findall(p, message_lower, re.IGNORECASE)) for p in patterns)
        
        if pattern_matches == 0:
            confidence -= 0.3  # No clear indicators
        elif pattern_matches >= 2:
            confidence += 0.1  # Strong indicators
        
        return max(0.1, min(1.0, confidence))
    
    def _generate_analysis_reasoning(self, task_type: TaskType, complexity: TaskComplexity, 
                                   recommended_model: Optional[str]) -> str:
        """Generate human-readable reasoning for the analysis"""
        reasoning_parts = [
            f"Classified as {task_type.value} task",
            f"Estimated complexity: {complexity.value}",
        ]
        
        if recommended_model:
            reasoning_parts.append(f"Recommended model: {recommended_model}")
        
        return ". ".join(reasoning_parts) + "."
    
    def _generate_optimization_suggestions(self, message: str, task_type: TaskType,
                                         complexity: TaskComplexity, estimated_tokens: int) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        # Token optimization
        if estimated_tokens > 4000:
            suggestions.append("Consider message fragmentation for better processing")
        
        # Model optimization
        if complexity == TaskComplexity.SIMPLE:
            suggestions.append("Use cost-optimized model selection for simple tasks")
        elif complexity == TaskComplexity.EXPERT:
            suggestions.append("Use most capable model for expert-level tasks")
        
        # Task-specific optimizations
        if task_type == TaskType.CODE_GENERATION:
            suggestions.append("Enable code-specific model optimizations")
        elif task_type == TaskType.ANALYSIS:
            suggestions.append("Provide structured output format for analysis tasks")
        
        return suggestions
    
    def _create_message_fragments(self, message: str, max_tokens: int) -> List[MessageFragment]:
        """Create message fragments from large message"""
        fragments = []
        
        # Simple sentence-based fragmentation
        sentences = re.split(r'[.!?]+', message)
        current_fragment = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_tokens = len(sentence.split()) * 1.3
            
            if current_tokens + sentence_tokens > max_tokens and current_fragment:
                # Create fragment
                fragment = MessageFragment(
                    fragment_id=self._generate_fragment_id(),
                    fragment_type=MessageFragmentType.INSTRUCTION,
                    content=current_fragment.strip(),
                    priority=len(fragments) + 1,
                    token_estimate=int(current_tokens),
                    dependencies=[]
                )
                fragments.append(fragment)
                
                # Start new fragment
                current_fragment = sentence
                current_tokens = sentence_tokens
            else:
                current_fragment += " " + sentence
                current_tokens += sentence_tokens
        
        # Add final fragment
        if current_fragment.strip():
            fragment = MessageFragment(
                fragment_id=self._generate_fragment_id(),
                fragment_type=MessageFragmentType.INSTRUCTION,
                content=current_fragment.strip(),
                priority=len(fragments) + 1,
                token_estimate=int(current_tokens),
                dependencies=[]
            )
            fragments.append(fragment)
        
        return fragments
    
    def _optimize_context_compression(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize context through compression"""
        # Placeholder for context compression logic
        return context
    
    def _optimize_model_routing(self, task_analysis: TaskAnalysis) -> str:
        """Optimize model routing based on task analysis"""
        # Placeholder for advanced model routing logic
        return task_analysis.recommended_model
    
    def _optimize_message_chunking(self, message: str) -> List[str]:
        """Optimize message chunking strategy"""
        # Placeholder for advanced chunking logic
        return [message]
    
    def _optimize_parallel_processing(self, fragments: List[MessageFragment]) -> List[MessageFragment]:
        """Optimize fragments for parallel processing"""
        # Placeholder for parallel processing optimization
        return fragments
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID"""
        return f"brain_task_{int(datetime.now().timestamp() * 1000)}"
    
    def _generate_fragment_id(self) -> str:
        """Generate unique fragment ID"""
        self.fragment_counter += 1
        return f"fragment_{self.fragment_counter:06d}"
    
    def _task_analysis_to_dict(self, analysis: TaskAnalysis) -> Dict[str, Any]:
        """Convert TaskAnalysis to dictionary"""
        return {
            'task_id': analysis.task_id,
            'task_type': analysis.task_type.value,
            'complexity': analysis.complexity.value,
            'estimated_tokens': analysis.estimated_tokens,
            'recommended_model': analysis.recommended_model,
            'confidence': analysis.confidence,
            'reasoning': analysis.reasoning,
            'optimization_suggestions': analysis.optimization_suggestions
        }
    
    def _fragment_to_dict(self, fragment: MessageFragment) -> Dict[str, Any]:
        """Convert MessageFragment to dictionary"""
        return {
            'fragment_id': fragment.fragment_id,
            'fragment_type': fragment.fragment_type.value,
            'content': fragment.content,
            'priority': fragment.priority,
            'token_estimate': fragment.token_estimate,
            'dependencies': fragment.dependencies
        }
    
    def _update_performance_metrics(self):
        """Update performance metrics periodically"""
        # Calculate average accuracy from recent tasks
        if self.learning_metrics['tasks_analyzed'] > 0:
            # Placeholder for accuracy calculation
            self.learning_metrics['average_accuracy'] = 0.85
        
        # Emit learning update
        self.learning_updated.emit(self.learning_metrics.copy())
    
    def get_brain_status(self) -> Dict[str, Any]:
        """Get brain AI manager status"""
        return {
            'learning_metrics': self.learning_metrics,
            'active_contexts': len(self.active_contexts),
            'optimization_strategies': list(self.optimization_strategies.keys()),
            'task_patterns_count': sum(len(patterns) for patterns in self.task_patterns.values()),
            'fragment_counter': self.fragment_counter
        }

# Singleton instance
_brain_ai_manager = None

def get_brain_ai_manager() -> BrainAIManager:
    """Get the singleton Brain AI Manager instance"""
    global _brain_ai_manager
    if _brain_ai_manager is None:
        _brain_ai_manager = BrainAIManager()
    return _brain_ai_manager
