#!/usr/bin/env python3
"""
Conversational AI Interface - Advanced Conversational AI System
Sprint 8.5 - Voice Commands and Natural Language Interface
Orion Vision Core - Autonomous AI Operating System

This module provides advanced conversational AI capabilities including
context-aware conversations, personality management, and intelligent
response generation for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.5.0
Date: 30 Mayıs 2025
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from .voice_manager import get_voice_manager
from ..nlp.natural_language_processor import get_natural_language_processor
from ..brain.brain_ai_manager import get_brain_ai_manager
from ..llm.llm_api_manager import get_llm_api_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConversationalAI")

class ConversationMode(Enum):
    """Conversation mode enumeration"""
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    ASSISTANT = "assistant"

class ResponseType(Enum):
    """Response type enumeration"""
    INFORMATIONAL = "informational"
    CONFIRMATIONAL = "confirmational"
    QUESTION = "question"
    COMMAND_RESPONSE = "command_response"
    ERROR_RESPONSE = "error_response"
    GREETING = "greeting"
    FAREWELL = "farewell"

class PersonalityTrait(Enum):
    """Personality trait enumeration"""
    HELPFUL = "helpful"
    CURIOUS = "curious"
    PATIENT = "patient"
    ENTHUSIASTIC = "enthusiastic"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ANALYTICAL = "analytical"

@dataclass
class ConversationContext:
    """Conversation context data"""
    conversation_id: str
    user_id: str
    start_time: datetime
    last_interaction: datetime
    mode: ConversationMode
    topic: Optional[str]
    intent_history: List[str]
    entity_memory: Dict[str, Any]
    user_preferences: Dict[str, Any]
    conversation_state: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationResponse:
    """Conversation response data"""
    response_id: str
    conversation_id: str
    response_text: str
    response_type: ResponseType
    confidence: float
    suggested_actions: List[str]
    context_updates: Dict[str, Any]
    emotion: str
    timestamp: datetime

class ConversationalAI(QObject):
    """
    Advanced conversational AI interface.
    
    Features:
    - Context-aware conversations
    - Personality management
    - Intelligent response generation
    - Multi-modal interaction
    - Conversation memory
    - Adaptive communication style
    """
    
    # Signals
    conversation_started = pyqtSignal(str, str)  # conversation_id, user_id
    response_generated = pyqtSignal(dict)  # ConversationResponse as dict
    context_updated = pyqtSignal(str, dict)  # conversation_id, context
    personality_changed = pyqtSignal(dict)  # personality_traits
    conversation_ended = pyqtSignal(str, str)  # conversation_id, reason
    
    def __init__(self):
        """Initialize Conversational AI"""
        super().__init__()
        
        # Component references
        self.voice_manager = get_voice_manager()
        self.nlp_processor = get_natural_language_processor()
        self.brain_manager = get_brain_ai_manager()
        self.llm_manager = get_llm_api_manager()
        
        # Conversational configuration
        self.default_mode = ConversationMode.ASSISTANT
        self.response_timeout = 30.0  # seconds
        self.context_memory_limit = 50  # interactions
        self.conversation_timeout = 3600.0  # 1 hour
        
        # Personality configuration
        self.personality_traits = {
            PersonalityTrait.HELPFUL: 0.9,
            PersonalityTrait.CURIOUS: 0.7,
            PersonalityTrait.PATIENT: 0.8,
            PersonalityTrait.ENTHUSIASTIC: 0.6,
            PersonalityTrait.PROFESSIONAL: 0.8,
            PersonalityTrait.FRIENDLY: 0.7,
            PersonalityTrait.ANALYTICAL: 0.8
        }
        
        # Response templates
        self.response_templates = {
            ResponseType.GREETING: [
                "Hello! How can I assist you today?",
                "Hi there! What can I help you with?",
                "Good to see you! How may I be of service?",
                "Welcome! I'm here to help with whatever you need."
            ],
            ResponseType.CONFIRMATIONAL: [
                "I understand. Let me take care of that for you.",
                "Got it! I'll handle that right away.",
                "Understood. Processing your request now.",
                "Perfect! I'm on it."
            ],
            ResponseType.QUESTION: [
                "Could you provide more details about that?",
                "I'd like to understand better. Can you elaborate?",
                "To help you better, could you clarify what you mean?",
                "What specific aspect would you like me to focus on?"
            ],
            ResponseType.ERROR_RESPONSE: [
                "I apologize, but I encountered an issue. Let me try a different approach.",
                "Something went wrong there. Could you try rephrasing your request?",
                "I'm having trouble with that. Would you mind trying again?",
                "That didn't work as expected. Let me help you find another way."
            ],
            ResponseType.FAREWELL: [
                "Goodbye! Feel free to ask if you need anything else.",
                "Take care! I'm here whenever you need assistance.",
                "See you later! Don't hesitate to reach out if you need help.",
                "Have a great day! I'll be here when you need me."
            ]
        }
        
        # Conversation management
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.conversation_history: List[ConversationContext] = []
        self.response_history: List[ConversationResponse] = []
        self.conversation_counter = 0
        self.response_counter = 0
        
        # Statistics
        self.conversation_stats = {
            'total_conversations': 0,
            'active_conversations': 0,
            'total_responses': 0,
            'average_conversation_length': 0.0,
            'response_types': {rt.value: 0 for rt in ResponseType},
            'conversation_modes': {cm.value: 0 for cm in ConversationMode},
            'average_response_time': 0.0,
            'user_satisfaction': 0.0
        }
        
        # Monitoring
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_conversations)
        self.cleanup_timer.start(300000)  # Cleanup every 5 minutes
        
        # Connect to voice manager signals
        self.voice_manager.voice_command_recognized.connect(self._handle_voice_command)
        
        logger.info("🤖 Conversational AI initialized")
    
    async def start_conversation(self, user_id: str, mode: ConversationMode = None,
                                initial_message: str = None) -> str:
        """
        Start a new conversation.
        
        Args:
            user_id: User identifier
            mode: Conversation mode
            initial_message: Initial message from user
            
        Returns:
            Conversation ID
        """
        try:
            conversation_id = self._generate_conversation_id()
            mode = mode or self.default_mode
            
            # Create conversation context
            context = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id,
                start_time=datetime.now(),
                last_interaction=datetime.now(),
                mode=mode,
                topic=None,
                intent_history=[],
                entity_memory={},
                user_preferences={},
                conversation_state="active"
            )
            
            # Store conversation
            self.active_conversations[conversation_id] = context
            
            # Update statistics
            self.conversation_stats['total_conversations'] += 1
            self.conversation_stats['active_conversations'] += 1
            self.conversation_stats['conversation_modes'][mode.value] += 1
            
            # Emit signal
            self.conversation_started.emit(conversation_id, user_id)
            
            # Generate greeting response
            if initial_message:
                await self.process_user_input(conversation_id, initial_message)
            else:
                greeting_response = await self._generate_greeting_response(context)
                await self._send_response(greeting_response)
            
            logger.info(f"🤖 Started conversation: {conversation_id} (user: {user_id}, mode: {mode.value})")
            return conversation_id
            
        except Exception as e:
            logger.error(f"❌ Error starting conversation: {e}")
            return None
    
    async def process_user_input(self, conversation_id: str, user_input: str) -> Optional[ConversationResponse]:
        """
        Process user input and generate response.
        
        Args:
            conversation_id: Conversation ID
            user_input: User input text
            
        Returns:
            ConversationResponse
        """
        try:
            if conversation_id not in self.active_conversations:
                logger.warning(f"⚠️ Conversation not found: {conversation_id}")
                return None
            
            context = self.active_conversations[conversation_id]
            start_time = datetime.now()
            
            # Update last interaction time
            context.last_interaction = datetime.now()
            
            # Process with NLP
            nlp_result = await self.nlp_processor.process_text(
                user_input, 
                conversation_id=conversation_id,
                context=context.metadata
            )
            
            # Update conversation context
            self._update_conversation_context(context, nlp_result)
            
            # Generate response based on intent and context
            response = await self._generate_contextual_response(context, nlp_result, user_input)
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self._update_conversation_stats(response, response_time)
            
            # Send response
            await self._send_response(response)
            
            # Store response in history
            self.response_history.append(response)
            if len(self.response_history) > 1000:  # Keep last 1000 responses
                self.response_history.pop(0)
            
            # Emit signals
            self.response_generated.emit(self._response_to_dict(response))
            self.context_updated.emit(conversation_id, self._context_to_dict(context))
            
            logger.info(f"🤖 Response generated for {conversation_id}: {response.response_type.value}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing user input: {e}")
            return await self._generate_error_response(conversation_id, str(e))
    
    async def _generate_contextual_response(self, context: ConversationContext,
                                          nlp_result, user_input: str) -> ConversationResponse:
        """Generate contextual response based on NLP result and conversation context"""
        try:
            response_id = self._generate_response_id()
            
            # Determine response type based on intent
            intent_type = nlp_result.intent.intent_type.value
            
            if intent_type == 'conversation':
                if any(greeting in user_input.lower() for greeting in ['hello', 'hi', 'hey']):
                    response_type = ResponseType.GREETING
                elif any(farewell in user_input.lower() for farewell in ['bye', 'goodbye', 'see you']):
                    response_type = ResponseType.FAREWELL
                else:
                    response_type = ResponseType.INFORMATIONAL
            elif intent_type in ['task_execution', 'workflow_creation', 'command_execution']:
                response_type = ResponseType.CONFIRMATIONAL
            elif intent_type in ['system_query', 'information_request']:
                response_type = ResponseType.INFORMATIONAL
            elif intent_type == 'help_request':
                response_type = ResponseType.QUESTION
            else:
                response_type = ResponseType.INFORMATIONAL
            
            # Generate response text
            response_text = await self._generate_response_text(
                context, nlp_result, response_type, user_input
            )
            
            # Generate suggested actions
            suggested_actions = self._generate_suggested_actions(nlp_result)
            
            # Determine emotion based on personality and context
            emotion = self._determine_response_emotion(context, nlp_result)
            
            # Create response
            response = ConversationResponse(
                response_id=response_id,
                conversation_id=context.conversation_id,
                response_text=response_text,
                response_type=response_type,
                confidence=nlp_result.confidence,
                suggested_actions=suggested_actions,
                context_updates={},
                emotion=emotion,
                timestamp=datetime.now()
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating contextual response: {e}")
            return await self._generate_error_response(context.conversation_id, str(e))
    
    async def _generate_response_text(self, context: ConversationContext,
                                    nlp_result, response_type: ResponseType,
                                    user_input: str) -> str:
        """Generate response text"""
        try:
            # Get base template
            templates = self.response_templates.get(response_type, ["I understand."])
            
            # Use brain manager for intelligent response generation
            if self.brain_manager:
                try:
                    brain_result = self.brain_manager.analyze_task(
                        f"Generate a {response_type.value} response to: '{user_input}' "
                        f"in {context.mode.value} mode with {self._get_personality_description()} personality"
                    )
                    
                    if brain_result and brain_result.optimization_suggestions:
                        return brain_result.optimization_suggestions[0]
                        
                except Exception as e:
                    logger.debug(f"Brain manager response generation failed: {e}")
            
            # Use LLM for advanced response generation
            if self.llm_manager:
                try:
                    prompt = self._create_response_prompt(context, nlp_result, response_type, user_input)
                    llm_response = await self.llm_manager.generate_response(prompt)
                    
                    if llm_response and llm_response.get('response'):
                        return llm_response['response']
                        
                except Exception as e:
                    logger.debug(f"LLM response generation failed: {e}")
            
            # Fallback to template-based response
            import random
            base_response = random.choice(templates)
            
            # Customize based on context
            if context.mode == ConversationMode.PROFESSIONAL:
                base_response = base_response.replace("Hi there!", "Good day,")
                base_response = base_response.replace("Hey", "Hello")
            elif context.mode == ConversationMode.FRIENDLY:
                base_response = base_response.replace("Hello", "Hey")
                base_response = base_response.replace("Good day", "Hi there")
            
            return base_response
            
        except Exception as e:
            logger.error(f"❌ Error generating response text: {e}")
            return "I'm here to help. How can I assist you?"
    
    def _create_response_prompt(self, context: ConversationContext, nlp_result,
                              response_type: ResponseType, user_input: str) -> str:
        """Create prompt for LLM response generation"""
        personality_desc = self._get_personality_description()
        
        prompt = f"""
        You are Orion, an AI assistant with the following personality: {personality_desc}
        
        Conversation Context:
        - Mode: {context.mode.value}
        - Topic: {context.topic or 'General'}
        - User Intent: {nlp_result.intent.intent_type.value}
        - Response Type: {response_type.value}
        
        User Input: "{user_input}"
        
        Generate a {response_type.value} response that is:
        - Appropriate for the {context.mode.value} conversation mode
        - Consistent with your personality traits
        - Helpful and relevant to the user's intent
        - Natural and conversational
        
        Response:
        """
        
        return prompt
    
    def _get_personality_description(self) -> str:
        """Get personality description based on traits"""
        strong_traits = [
            trait.value for trait, strength in self.personality_traits.items()
            if strength > 0.7
        ]
        return ", ".join(strong_traits) if strong_traits else "balanced"
    
    def _generate_suggested_actions(self, nlp_result) -> List[str]:
        """Generate suggested actions based on NLP result"""
        actions = []
        
        intent_type = nlp_result.intent.intent_type.value
        
        if intent_type == 'task_execution':
            actions.extend([
                "View task details",
                "Monitor task progress",
                "Cancel task if needed"
            ])
        elif intent_type == 'workflow_creation':
            actions.extend([
                "Add more steps",
                "Set dependencies",
                "Configure automation"
            ])
        elif intent_type == 'system_query':
            actions.extend([
                "View detailed metrics",
                "Export system report",
                "Set up monitoring"
            ])
        elif intent_type == 'file_operation':
            actions.extend([
                "Open file location",
                "View file properties",
                "Create backup"
            ])
        
        return actions[:3]  # Limit to 3 suggestions
    
    def _determine_response_emotion(self, context: ConversationContext, nlp_result) -> str:
        """Determine response emotion based on context and personality"""
        # Base emotion on personality traits
        if self.personality_traits[PersonalityTrait.ENTHUSIASTIC] > 0.7:
            return "enthusiastic"
        elif self.personality_traits[PersonalityTrait.PROFESSIONAL] > 0.8:
            return "professional"
        elif self.personality_traits[PersonalityTrait.FRIENDLY] > 0.7:
            return "friendly"
        else:
            return "neutral"
    
    async def _generate_greeting_response(self, context: ConversationContext) -> ConversationResponse:
        """Generate greeting response for new conversation"""
        response_id = self._generate_response_id()
        
        greeting_text = await self._generate_response_text(
            context, None, ResponseType.GREETING, "Hello"
        )
        
        return ConversationResponse(
            response_id=response_id,
            conversation_id=context.conversation_id,
            response_text=greeting_text,
            response_type=ResponseType.GREETING,
            confidence=1.0,
            suggested_actions=["Ask a question", "Request help", "Start a task"],
            context_updates={},
            emotion="friendly",
            timestamp=datetime.now()
        )
    
    async def _generate_error_response(self, conversation_id: str, error_message: str) -> ConversationResponse:
        """Generate error response"""
        response_id = self._generate_response_id()
        
        import random
        error_templates = self.response_templates[ResponseType.ERROR_RESPONSE]
        response_text = random.choice(error_templates)
        
        return ConversationResponse(
            response_id=response_id,
            conversation_id=conversation_id,
            response_text=response_text,
            response_type=ResponseType.ERROR_RESPONSE,
            confidence=0.5,
            suggested_actions=["Try again", "Rephrase request", "Ask for help"],
            context_updates={},
            emotion="apologetic",
            timestamp=datetime.now()
        )
    
    async def _send_response(self, response: ConversationResponse):
        """Send response via voice synthesis"""
        try:
            # Use voice manager to speak the response
            await self.voice_manager.speak(
                text=response.response_text,
                emotion=response.emotion,
                priority=7  # High priority for conversation responses
            )
            
        except Exception as e:
            logger.error(f"❌ Error sending response: {e}")
    
    def _update_conversation_context(self, context: ConversationContext, nlp_result):
        """Update conversation context with NLP result"""
        try:
            # Update intent history
            context.intent_history.append(nlp_result.intent.intent_type.value)
            if len(context.intent_history) > 10:  # Keep last 10 intents
                context.intent_history.pop(0)
            
            # Update entity memory
            for entity in nlp_result.entities:
                context.entity_memory[entity.entity_type.value] = entity.value
            
            # Update topic if it's a significant intent
            if nlp_result.intent.intent_type.value not in ['conversation', 'help_request']:
                context.topic = nlp_result.intent.intent_type.value
            
        except Exception as e:
            logger.error(f"❌ Error updating conversation context: {e}")
    
    def _handle_voice_command(self, command_data: Dict[str, Any]):
        """Handle voice command from voice manager"""
        try:
            # Find or create conversation for this command
            # For simplicity, we'll use a default conversation
            conversation_id = "voice_conversation"
            
            if conversation_id not in self.active_conversations:
                asyncio.create_task(self.start_conversation("voice_user", ConversationMode.ASSISTANT))
            
            # Process the voice command as user input
            original_text = command_data.get('original_text', '')
            if original_text:
                asyncio.create_task(self.process_user_input(conversation_id, original_text))
                
        except Exception as e:
            logger.error(f"❌ Error handling voice command: {e}")
    
    def _cleanup_expired_conversations(self):
        """Clean up expired conversations"""
        try:
            current_time = datetime.now()
            expired_conversations = []
            
            for conv_id, context in self.active_conversations.items():
                time_since_last = (current_time - context.last_interaction).total_seconds()
                if time_since_last > self.conversation_timeout:
                    expired_conversations.append(conv_id)
            
            for conv_id in expired_conversations:
                context = self.active_conversations.pop(conv_id)
                self.conversation_history.append(context)
                self.conversation_stats['active_conversations'] -= 1
                self.conversation_ended.emit(conv_id, "timeout")
                
                logger.info(f"🤖 Conversation expired: {conv_id}")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up conversations: {e}")
    
    def _update_conversation_stats(self, response: ConversationResponse, response_time: float):
        """Update conversation statistics"""
        self.conversation_stats['total_responses'] += 1
        self.conversation_stats['response_types'][response.response_type.value] += 1
        
        # Update average response time
        total_responses = self.conversation_stats['total_responses']
        current_avg = self.conversation_stats['average_response_time']
        new_avg = ((current_avg * (total_responses - 1)) + response_time) / total_responses
        self.conversation_stats['average_response_time'] = new_avg
    
    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID"""
        self.conversation_counter += 1
        return f"conv_{self.conversation_counter:06d}"
    
    def _generate_response_id(self) -> str:
        """Generate unique response ID"""
        self.response_counter += 1
        return f"resp_{self.response_counter:06d}"
    
    def _context_to_dict(self, context: ConversationContext) -> Dict[str, Any]:
        """Convert ConversationContext to dictionary"""
        return {
            'conversation_id': context.conversation_id,
            'user_id': context.user_id,
            'start_time': context.start_time.isoformat(),
            'last_interaction': context.last_interaction.isoformat(),
            'mode': context.mode.value,
            'topic': context.topic,
            'intent_history': context.intent_history,
            'entity_memory': context.entity_memory,
            'conversation_state': context.conversation_state
        }
    
    def _response_to_dict(self, response: ConversationResponse) -> Dict[str, Any]:
        """Convert ConversationResponse to dictionary"""
        return {
            'response_id': response.response_id,
            'conversation_id': response.conversation_id,
            'response_text': response.response_text,
            'response_type': response.response_type.value,
            'confidence': response.confidence,
            'suggested_actions': response.suggested_actions,
            'emotion': response.emotion,
            'timestamp': response.timestamp.isoformat()
        }
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        return self.conversation_stats.copy()
    
    def get_active_conversations(self) -> List[Dict[str, Any]]:
        """Get active conversations"""
        return [self._context_to_dict(context) for context in self.active_conversations.values()]
    
    def set_personality_trait(self, trait: PersonalityTrait, strength: float):
        """Set personality trait strength"""
        self.personality_traits[trait] = max(0.0, min(1.0, strength))
        self.personality_changed.emit({trait.value: strength for trait, strength in self.personality_traits.items()})
        logger.info(f"🤖 Personality trait updated: {trait.value} = {strength}")

# Singleton instance
_conversational_ai = None

def get_conversational_ai() -> ConversationalAI:
    """Get the singleton Conversational AI instance"""
    global _conversational_ai
    if _conversational_ai is None:
        _conversational_ai = ConversationalAI()
    return _conversational_ai
