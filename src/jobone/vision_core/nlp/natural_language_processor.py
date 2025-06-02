#!/usr/bin/env python3
"""
Natural Language Processor - Advanced NLP and Intent Recognition
Sprint 8.5 - Voice Commands and Natural Language Interface
Orion Vision Core - Autonomous AI Operating System

This module provides advanced natural language processing capabilities including
intent recognition, entity extraction, and conversational AI for the
Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.5.0
Date: 30 Mayıs 2025
"""

import logging
import asyncio
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

from ..brain.brain_ai_manager import get_brain_ai_manager
from ..llm.llm_api_manager import get_llm_api_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NaturalLanguageProcessor")

class IntentType(Enum):
    """Intent type enumeration"""
    TASK_EXECUTION = "task_execution"
    WORKFLOW_CREATION = "workflow_creation"
    SYSTEM_QUERY = "system_query"
    FILE_OPERATION = "file_operation"
    AUTOMATION_SETUP = "automation_setup"
    INFORMATION_REQUEST = "information_request"
    CONVERSATION = "conversation"
    COMMAND_EXECUTION = "command_execution"
    HELP_REQUEST = "help_request"
    UNKNOWN = "unknown"

class EntityType(Enum):
    """Entity type enumeration"""
    TASK_NAME = "task_name"
    FILE_PATH = "file_path"
    COMMAND = "command"
    PARAMETER = "parameter"
    TIME = "time"
    NUMBER = "number"
    PERSON = "person"
    LOCATION = "location"
    SYSTEM_COMPONENT = "system_component"

class LanguageModel(Enum):
    """Language model enumeration"""
    SIMPLE_RULES = "simple_rules"
    PATTERN_MATCHING = "pattern_matching"
    MACHINE_LEARNING = "machine_learning"
    TRANSFORMER = "transformer"
    HYBRID = "hybrid"

@dataclass
class Entity:
    """Extracted entity"""
    entity_type: EntityType
    value: str
    confidence: float
    start_position: int
    end_position: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Intent:
    """Recognized intent"""
    intent_type: IntentType
    confidence: float
    entities: List[Entity]
    parameters: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NLPResult:
    """Natural language processing result"""
    processing_id: str
    original_text: str
    normalized_text: str
    intent: Intent
    entities: List[Entity]
    sentiment: Dict[str, float]
    language: str
    confidence: float
    processing_time: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

class NaturalLanguageProcessor(QObject):
    """
    Advanced natural language processing system.
    
    Features:
    - Intent recognition and classification
    - Entity extraction and normalization
    - Sentiment analysis
    - Language detection
    - Conversational context management
    - Multi-language support
    """
    
    # Signals
    intent_recognized = pyqtSignal(dict)  # Intent as dict
    entity_extracted = pyqtSignal(dict)  # Entity as dict
    nlp_completed = pyqtSignal(dict)  # NLPResult as dict
    conversation_updated = pyqtSignal(str, dict)  # conversation_id, context
    
    def __init__(self):
        """Initialize Natural Language Processor"""
        super().__init__()
        
        # Component references
        self.brain_manager = get_brain_ai_manager()
        self.llm_manager = get_llm_api_manager()
        
        # NLP configuration
        self.language_model = LanguageModel.HYBRID
        self.default_language = "en"
        self.confidence_threshold = 0.6
        self.max_entities_per_text = 20
        
        # Intent patterns
        self.intent_patterns = {
            IntentType.TASK_EXECUTION: [
                r"(run|execute|start|perform|do) (task|job|work)",
                r"(begin|initiate|launch) (the )?task",
                r"(carry out|complete) (the )?task"
            ],
            IntentType.WORKFLOW_CREATION: [
                r"(create|build|make|design) (a |new )?workflow",
                r"(set up|establish) (a )?workflow",
                r"(generate|construct) workflow"
            ],
            IntentType.SYSTEM_QUERY: [
                r"(what is|how is|show me) (the )?system (status|health|state)",
                r"(check|verify|monitor) system",
                r"(system|health|status) (report|check|info)"
            ],
            IntentType.FILE_OPERATION: [
                r"(create|make|generate) (a |new )?file",
                r"(open|read|view|show) (the )?file",
                r"(delete|remove|erase) (the )?file",
                r"(copy|duplicate|move|transfer) (the )?file"
            ],
            IntentType.AUTOMATION_SETUP: [
                r"(automate|schedule|set up automation)",
                r"(create|make) (an )?automation (rule|task)",
                r"(automatically|auto) (run|execute|perform)"
            ],
            IntentType.INFORMATION_REQUEST: [
                r"(what|how|when|where|why|who)",
                r"(tell me|show me|explain|describe)",
                r"(information|details|data) (about|on|regarding)"
            ],
            IntentType.CONVERSATION: [
                r"(hello|hi|hey|greetings)",
                r"(how are you|how do you do)",
                r"(thank you|thanks|goodbye|bye)"
            ],
            IntentType.COMMAND_EXECUTION: [
                r"(run|execute) (command|cmd)",
                r"(terminal|console|shell) (command|cmd)",
                r"(use|invoke) (the )?command (line|prompt)"
            ],
            IntentType.HELP_REQUEST: [
                r"(help|assist|support|guide)",
                r"(what can you do|capabilities|features)",
                r"(how to|how do I|instructions)"
            ]
        }
        
        # Entity patterns
        self.entity_patterns = {
            EntityType.TASK_NAME: [
                r"task (\w+)",
                r"job (\w+)",
                r"work (\w+)"
            ],
            EntityType.FILE_PATH: [
                r"file ([/\w\.-]+)",
                r"path ([/\w\.-]+)",
                r"([/\w\.-]+\.\w+)"
            ],
            EntityType.COMMAND: [
                r"command (\w+)",
                r"cmd (\w+)",
                r"run (\w+)"
            ],
            EntityType.TIME: [
                r"(\d{1,2}:\d{2})",
                r"(in \d+ (minutes|hours|days))",
                r"(at \d{1,2} (am|pm))"
            ],
            EntityType.NUMBER: [
                r"(\d+)",
                r"(one|two|three|four|five|six|seven|eight|nine|ten)"
            ]
        }
        
        # Sentiment keywords
        self.positive_keywords = [
            "good", "great", "excellent", "awesome", "perfect", "wonderful",
            "amazing", "fantastic", "brilliant", "outstanding", "superb"
        ]
        
        self.negative_keywords = [
            "bad", "terrible", "awful", "horrible", "poor", "disappointing",
            "frustrating", "annoying", "useless", "broken", "failed"
        ]
        
        # Conversation context
        self.conversation_contexts: Dict[str, Dict[str, Any]] = {}
        self.processing_history: List[NLPResult] = []
        self.processing_counter = 0
        
        # Statistics
        self.nlp_stats = {
            'total_processed': 0,
            'successful_processed': 0,
            'failed_processed': 0,
            'intents_by_type': {intent.value: 0 for intent in IntentType},
            'entities_by_type': {entity.value: 0 for entity in EntityType},
            'average_confidence': 0.0,
            'average_processing_time': 0.0,
            'languages_detected': {}
        }
        
        logger.info("🧠 Natural Language Processor initialized")
    
    async def process_text(self, text: str, conversation_id: str = None,
                          context: Dict[str, Any] = None) -> NLPResult:
        """
        Process natural language text.
        
        Args:
            text: Text to process
            conversation_id: Conversation ID for context
            context: Additional context information
            
        Returns:
            NLPResult with processing results
        """
        try:
            processing_id = self._generate_processing_id()
            start_time = datetime.now()
            
            # Normalize text
            normalized_text = self._normalize_text(text)
            
            # Detect language
            language = self._detect_language(normalized_text)
            
            # Recognize intent
            intent = await self._recognize_intent(normalized_text, context)
            
            # Extract entities
            entities = self._extract_entities(normalized_text)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(normalized_text)
            
            # Calculate overall confidence
            confidence = self._calculate_overall_confidence(intent, entities)
            
            # Calculate processing time
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # Create result
            result = NLPResult(
                processing_id=processing_id,
                original_text=text,
                normalized_text=normalized_text,
                intent=intent,
                entities=entities,
                sentiment=sentiment,
                language=language,
                confidence=confidence,
                processing_time=processing_time,
                timestamp=start_time,
                success=True
            )
            
            # Update conversation context
            if conversation_id:
                self._update_conversation_context(conversation_id, result)
            
            # Store in history
            self.processing_history.append(result)
            if len(self.processing_history) > 1000:  # Keep last 1000 results
                self.processing_history.pop(0)
            
            # Update statistics
            self._update_nlp_stats(result)
            
            # Emit signals
            self.intent_recognized.emit(self._intent_to_dict(intent))
            for entity in entities:
                self.entity_extracted.emit(self._entity_to_dict(entity))
            self.nlp_completed.emit(self._nlp_result_to_dict(result))
            
            logger.info(f"🧠 NLP processed: {intent.intent_type.value} "
                       f"(confidence: {confidence:.3f}, entities: {len(entities)})")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing text: {e}")
            return NLPResult(
                processing_id=self._generate_processing_id(),
                original_text=text,
                normalized_text=text,
                intent=Intent(IntentType.UNKNOWN, 0.0, [], {}),
                entities=[],
                sentiment={'positive': 0.0, 'negative': 0.0, 'neutral': 1.0},
                language=self.default_language,
                confidence=0.0,
                processing_time=0.0,
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for processing"""
        try:
            # Convert to lowercase
            normalized = text.lower().strip()
            
            # Remove extra whitespace
            normalized = re.sub(r'\s+', ' ', normalized)
            
            # Remove special characters (keep basic punctuation)
            normalized = re.sub(r'[^\w\s\.\,\?\!\-]', '', normalized)
            
            # Expand contractions
            contractions = {
                "don't": "do not",
                "won't": "will not",
                "can't": "cannot",
                "n't": " not",
                "'re": " are",
                "'ve": " have",
                "'ll": " will",
                "'d": " would"
            }
            
            for contraction, expansion in contractions.items():
                normalized = normalized.replace(contraction, expansion)
            
            return normalized
            
        except Exception as e:
            logger.error(f"❌ Error normalizing text: {e}")
            return text.lower().strip()
    
    def _detect_language(self, text: str) -> str:
        """Detect text language (simplified implementation)"""
        try:
            # Simple language detection based on common words
            english_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
            turkish_words = ["ve", "veya", "ama", "ile", "için", "den", "dan", "da", "de", "bir", "bu", "şu"]
            
            words = text.split()
            english_count = sum(1 for word in words if word in english_words)
            turkish_count = sum(1 for word in words if word in turkish_words)
            
            if turkish_count > english_count:
                return "tr"
            else:
                return "en"
                
        except Exception:
            return self.default_language
    
    async def _recognize_intent(self, text: str, context: Dict[str, Any] = None) -> Intent:
        """Recognize intent from text"""
        try:
            best_intent = IntentType.UNKNOWN
            best_confidence = 0.0
            parameters = {}
            
            # Pattern-based intent recognition
            for intent_type, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        # Calculate confidence based on match quality
                        confidence = len(match.group(0)) / len(text)
                        confidence = min(1.0, confidence * 2.0)  # Boost confidence
                        
                        if confidence > best_confidence:
                            best_intent = intent_type
                            best_confidence = confidence
                            
                            # Extract parameters from match groups
                            if match.groups():
                                parameters['matched_groups'] = match.groups()
            
            # Use brain manager for advanced intent recognition
            if best_confidence < 0.7 and self.brain_manager:
                try:
                    brain_result = self.brain_manager.analyze_task(
                        f"Classify the intent of this text: '{text}'"
                    )
                    
                    if brain_result and brain_result.task_type:
                        # Map brain result to intent type
                        intent_mapping = {
                            'automation': IntentType.TASK_EXECUTION,
                            'analysis': IntentType.INFORMATION_REQUEST,
                            'system_command': IntentType.COMMAND_EXECUTION,
                            'file_operation': IntentType.FILE_OPERATION
                        }
                        
                        mapped_intent = intent_mapping.get(brain_result.task_type.value, IntentType.UNKNOWN)
                        if mapped_intent != IntentType.UNKNOWN:
                            best_intent = mapped_intent
                            best_confidence = max(best_confidence, 0.8)
                            
                except Exception as e:
                    logger.debug(f"Brain manager intent recognition failed: {e}")
            
            # Ensure minimum confidence for known patterns
            if best_intent != IntentType.UNKNOWN and best_confidence < 0.5:
                best_confidence = 0.5
            
            return Intent(
                intent_type=best_intent,
                confidence=best_confidence,
                entities=[],  # Will be filled by entity extraction
                parameters=parameters,
                context=context or {}
            )
            
        except Exception as e:
            logger.error(f"❌ Error recognizing intent: {e}")
            return Intent(IntentType.UNKNOWN, 0.0, [], {})
    
    def _extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text"""
        try:
            entities = []
            
            # Pattern-based entity extraction
            for entity_type, patterns in self.entity_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        entity = Entity(
                            entity_type=entity_type,
                            value=match.group(1) if match.groups() else match.group(0),
                            confidence=0.8,  # Pattern-based confidence
                            start_position=match.start(),
                            end_position=match.end()
                        )
                        entities.append(entity)
            
            # Remove duplicates and overlapping entities
            entities = self._remove_overlapping_entities(entities)
            
            # Limit number of entities
            entities = entities[:self.max_entities_per_text]
            
            return entities
            
        except Exception as e:
            logger.error(f"❌ Error extracting entities: {e}")
            return []
    
    def _remove_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove overlapping entities, keeping the highest confidence ones"""
        if not entities:
            return entities
        
        # Sort by confidence (descending)
        entities.sort(key=lambda e: e.confidence, reverse=True)
        
        filtered_entities = []
        for entity in entities:
            # Check if this entity overlaps with any already selected entity
            overlaps = False
            for selected_entity in filtered_entities:
                if (entity.start_position < selected_entity.end_position and
                    entity.end_position > selected_entity.start_position):
                    overlaps = True
                    break
            
            if not overlaps:
                filtered_entities.append(entity)
        
        # Sort by position
        filtered_entities.sort(key=lambda e: e.start_position)
        
        return filtered_entities
    
    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of text"""
        try:
            words = text.split()
            positive_count = sum(1 for word in words if word in self.positive_keywords)
            negative_count = sum(1 for word in words if word in self.negative_keywords)
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
            
            positive_score = positive_count / total_sentiment_words
            negative_score = negative_count / total_sentiment_words
            neutral_score = 1.0 - positive_score - negative_score
            
            return {
                'positive': positive_score,
                'negative': negative_score,
                'neutral': max(0.0, neutral_score)
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing sentiment: {e}")
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
    
    def _calculate_overall_confidence(self, intent: Intent, entities: List[Entity]) -> float:
        """Calculate overall confidence score"""
        try:
            intent_confidence = intent.confidence
            
            if entities:
                entity_confidence = sum(e.confidence for e in entities) / len(entities)
                # Weighted average: 70% intent, 30% entities
                overall_confidence = (intent_confidence * 0.7) + (entity_confidence * 0.3)
            else:
                overall_confidence = intent_confidence
            
            return min(1.0, overall_confidence)
            
        except Exception:
            return 0.5
    
    def _update_conversation_context(self, conversation_id: str, result: NLPResult):
        """Update conversation context"""
        try:
            if conversation_id not in self.conversation_contexts:
                self.conversation_contexts[conversation_id] = {
                    'history': [],
                    'current_topic': None,
                    'entities': {},
                    'last_intent': None,
                    'created_at': datetime.now().isoformat()
                }
            
            context = self.conversation_contexts[conversation_id]
            
            # Add to history
            context['history'].append({
                'text': result.original_text,
                'intent': result.intent.intent_type.value,
                'timestamp': result.timestamp.isoformat()
            })
            
            # Keep last 10 interactions
            if len(context['history']) > 10:
                context['history'].pop(0)
            
            # Update current topic
            if result.intent.intent_type != IntentType.CONVERSATION:
                context['current_topic'] = result.intent.intent_type.value
            
            # Update entities
            for entity in result.entities:
                context['entities'][entity.entity_type.value] = entity.value
            
            # Update last intent
            context['last_intent'] = result.intent.intent_type.value
            
            # Emit context update
            self.conversation_updated.emit(conversation_id, context)
            
        except Exception as e:
            logger.error(f"❌ Error updating conversation context: {e}")
    
    def _update_nlp_stats(self, result: NLPResult):
        """Update NLP statistics"""
        self.nlp_stats['total_processed'] += 1
        
        if result.success:
            self.nlp_stats['successful_processed'] += 1
        else:
            self.nlp_stats['failed_processed'] += 1
        
        # Update intent statistics
        self.nlp_stats['intents_by_type'][result.intent.intent_type.value] += 1
        
        # Update entity statistics
        for entity in result.entities:
            self.nlp_stats['entities_by_type'][entity.entity_type.value] += 1
        
        # Update language statistics
        if result.language not in self.nlp_stats['languages_detected']:
            self.nlp_stats['languages_detected'][result.language] = 0
        self.nlp_stats['languages_detected'][result.language] += 1
        
        # Update averages
        total = self.nlp_stats['total_processed']
        
        # Average confidence
        current_avg_conf = self.nlp_stats['average_confidence']
        new_avg_conf = ((current_avg_conf * (total - 1)) + result.confidence) / total
        self.nlp_stats['average_confidence'] = new_avg_conf
        
        # Average processing time
        current_avg_time = self.nlp_stats['average_processing_time']
        new_avg_time = ((current_avg_time * (total - 1)) + result.processing_time) / total
        self.nlp_stats['average_processing_time'] = new_avg_time
    
    def _generate_processing_id(self) -> str:
        """Generate unique processing ID"""
        self.processing_counter += 1
        return f"nlp_{self.processing_counter:06d}"
    
    def _intent_to_dict(self, intent: Intent) -> Dict[str, Any]:
        """Convert Intent to dictionary"""
        return {
            'intent_type': intent.intent_type.value,
            'confidence': intent.confidence,
            'parameters': intent.parameters,
            'context': intent.context
        }
    
    def _entity_to_dict(self, entity: Entity) -> Dict[str, Any]:
        """Convert Entity to dictionary"""
        return {
            'entity_type': entity.entity_type.value,
            'value': entity.value,
            'confidence': entity.confidence,
            'start_position': entity.start_position,
            'end_position': entity.end_position,
            'metadata': entity.metadata
        }
    
    def _nlp_result_to_dict(self, result: NLPResult) -> Dict[str, Any]:
        """Convert NLPResult to dictionary"""
        return {
            'processing_id': result.processing_id,
            'original_text': result.original_text,
            'normalized_text': result.normalized_text,
            'intent': self._intent_to_dict(result.intent),
            'entities': [self._entity_to_dict(e) for e in result.entities],
            'sentiment': result.sentiment,
            'language': result.language,
            'confidence': result.confidence,
            'processing_time': result.processing_time,
            'timestamp': result.timestamp.isoformat(),
            'success': result.success,
            'error_message': result.error_message
        }
    
    def get_nlp_stats(self) -> Dict[str, Any]:
        """Get NLP statistics"""
        return self.nlp_stats.copy()
    
    def get_processing_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get processing history"""
        history = self.processing_history[-limit:] if limit > 0 else self.processing_history
        return [self._nlp_result_to_dict(result) for result in history]
    
    def get_conversation_context(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation context"""
        return self.conversation_contexts.get(conversation_id)
    
    def clear_conversation_context(self, conversation_id: str) -> bool:
        """Clear conversation context"""
        if conversation_id in self.conversation_contexts:
            del self.conversation_contexts[conversation_id]
            return True
        return False

# Singleton instance
_natural_language_processor = None

def get_natural_language_processor() -> NaturalLanguageProcessor:
    """Get the singleton Natural Language Processor instance"""
    global _natural_language_processor
    if _natural_language_processor is None:
        _natural_language_processor = NaturalLanguageProcessor()
    return _natural_language_processor
